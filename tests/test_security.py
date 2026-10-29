"""JWT 발급·검증(PyJWT)과 JWT 비밀키 검사를 고정한다.

python-jose(3.5.0, 고친 판이 없는 권고 GHSA-3qf3-8w2g-rqmx)를 PyJWT로 바꾸면서 넣은 테스트다. 바꾸기 전에
python-jose로 만든 토큰을 그대로 적어 두고, 바꾼 뒤에도 같은 토큰이 풀리고 같은 클레임이면 같은 문자열이
나오는지 본다. 이미 발급된 토큰(접근 30분, 갱신 7일)이 교체 뒤에도 그대로 쓰여야 하기 때문이다.
"""

# [테스트 묶음] app/services/security.py의 토큰 함수·이메일 지문, app/config.py의 JWT 비밀키 검사, 관리자 토큰
# 검사(app/dependencies.py의 require_admin_token)가 남기는 감사 로그. DB가 필요 없다.
# [왜 중요한가]
# - 토큰 형식이 바뀌면 배포 순간 모든 사용자가 로그아웃된다. 머리글·클레임·서명이 바이트 단위로 같아야 한다.
# - 알고리즘을 HS256 하나로 고정해야 'alg: none'이나 다른 알고리즘을 주장하는 토큰을 받지 않는다.
# - 서명이 맞아도 sub가 UUID가 아닌 토큰은 500이 아니라 401(InvalidTokenError)이어야 한다.
# - 공개 예시 비밀키(.env.example 값)로 서명하면 누구나 토큰을 만들 수 있다. 기본은 경고,
#   APP_ENV=production이면 시작 거부다. CI 워크플로의 비밀키도 저장소에 공개된 값이라 같은 취급을 한다.
# - 비밀키 최소 길이는 서명 알고리즘의 해시 출력 길이다(HS256 32, HS384 48, HS512 64바이트).
# - 감사 로그에는 이메일 원문·토큰 값이 들어가면 안 된다(이메일은 지문, 토큰은 아예 적지 않음).

import hashlib
import logging
import re
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path

# jwt: PyJWT. 테스트에서 일부러 잘못된 토큰(다른 알고리즘, 만료, 클레임 빠짐)을 만들 때만 직접 쓴다.
# get_default_algorithms: PyJWT가 알고리즘마다 쓰는 해시(키 길이 경고 기준)를 읽을 때 쓴다.
import jwt
import pytest
from fastapi import HTTPException, Request
from jwt.algorithms import get_default_algorithms
from pydantic import ValidationError

from app.config import (
    MIN_JWT_SECRET_BYTES,
    PUBLIC_EXAMPLE_JWT_SECRETS,
    Settings,
    jwt_secret_problem,
    warn_if_weak_jwt_secret,
)
from app.dependencies import require_admin_token
from app.services import security
from app.services.security import InvalidTokenError, TokenType, decode_token, email_fingerprint

# python-jose 3.5.0으로 2026-10-15에 만든 토큰(교체 전 마지막 판). 비밀키·클레임은 아래 상수와 같다. exp는
# 2100-01-01이라 테스트가 오래 지나도 만료되지 않는다.
JOSE_SECRET = "test-secret-for-jose-compat-0123456789"
JOSE_SUBJECT = uuid.UUID("3f2c9d4e-8a1b-4c5d-9e6f-0a1b2c3d4e5f")
JOSE_IAT = datetime(2026, 10, 15, 0, 0, tzinfo=UTC)
JOSE_EXP = datetime(2100, 1, 1, 0, 0, tzinfo=UTC)
JOSE_ACCESS_TOKEN = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJzdWIiOiIzZjJjOWQ0ZS04YTFiLTRjNWQtOWU2Zi0wYTFiMmMzZDRlNWYiLCJ0eXBlIjoiYWNjZXNzIiwiaWF0IjoxNzkyMDIyNDAwLCJleHAiOjQxMDI0NDQ4MDB9."
    "2yFtFMmTyM7fF2AP7aK7ElILWXFow3i68ZJvzwiz3fo"
)


# security 모듈이 import 때 읽은 설정의 비밀키를 테스트용 값으로 바꾼다. 알고리즘은 기본값 HS256 그대로다.
@pytest.fixture
def jose_secret(monkeypatch):
    monkeypatch.setattr(security.settings, "jwt_secret_key", JOSE_SECRET)
    monkeypatch.setattr(security.settings, "jwt_algorithm", "HS256")


# 같은 비밀키로 서명한 임의의 클레임 토큰(잘못된 토큰을 만들 때 쓴다).
def _signed(payload: dict, algorithm: str = "HS256") -> str:
    return jwt.encode(payload, JOSE_SECRET, algorithm=algorithm)


# 교체 전(python-jose)에 발급된 접근 토큰이 교체 뒤에도 같은 사용자로 풀린다.
def test_a_token_issued_by_python_jose_still_decodes(jose_secret):
    assert decode_token(JOSE_ACCESS_TOKEN, TokenType.ACCESS) == JOSE_SUBJECT


# 같은 클레임·비밀키면 새 코드가 python-jose와 바이트 단위로 같은 토큰을 만든다(머리글 키 정렬, 숫자
# 타임스탬프, 같은 JSON 구분자).
def test_new_tokens_are_byte_identical_to_python_jose_tokens(jose_secret):
    token = security._create_token(JOSE_SUBJECT, TokenType.ACCESS, JOSE_EXP - JOSE_IAT, now=JOSE_IAT)
    assert token == JOSE_ACCESS_TOKEN


# 새로 만든 접근·갱신 토큰을 왕복하고, 종류가 다르면 거부한다(갱신 토큰을 접근 토큰 자리에 쓸 수 없음).
def test_round_trip_and_type_check(jose_secret):
    user_id = uuid.uuid4()
    assert decode_token(security.create_access_token(user_id), TokenType.ACCESS) == user_id
    assert decode_token(security.create_refresh_token(user_id), TokenType.REFRESH) == user_id
    with pytest.raises(InvalidTokenError):
        decode_token(security.create_refresh_token(user_id), TokenType.ACCESS)


# HS256이 아닌 토큰은 서명이 맞아도 거부한다: 'alg: none'(서명 없음)과 같은 비밀키로 서명한 HS512. 테스트
# 키가 HS512 권장 길이(64바이트)보다 짧아 PyJWT가 내는 경고는 이 테스트에서만 끈다.
@pytest.mark.filterwarnings("ignore::jwt.InsecureKeyLengthWarning")
@pytest.mark.parametrize("algorithm", ["none", "HS512"])
def test_tokens_with_another_algorithm_are_rejected(jose_secret, algorithm):
    payload = {"sub": str(JOSE_SUBJECT), "type": "access", "iat": JOSE_IAT, "exp": JOSE_EXP}
    token = jwt.encode(payload, None if algorithm == "none" else JOSE_SECRET, algorithm=algorithm)
    with pytest.raises(InvalidTokenError):
        decode_token(token, TokenType.ACCESS)


# 서명을 바꾼 토큰, 만료된 토큰, 모양이 깨진 문자열은 모두 같은 InvalidTokenError(라우터에서 401)가 된다.
def test_tampered_expired_and_malformed_tokens_are_rejected(jose_secret):
    tampered = JOSE_ACCESS_TOKEN[:-2] + ("AA" if not JOSE_ACCESS_TOKEN.endswith("AA") else "BB")
    expired = _signed(
        {
            "sub": str(JOSE_SUBJECT),
            "type": "access",
            "iat": datetime(2000, 1, 1, tzinfo=UTC),
            "exp": datetime(2000, 1, 1, tzinfo=UTC) + timedelta(minutes=30),
        }
    )
    for token in (tampered, expired, "not-a-jwt", "", "a.b.c"):
        with pytest.raises(InvalidTokenError):
            decode_token(token, TokenType.ACCESS)


# 이 앱이 발급하는 토큰에는 늘 exp·iat·sub가 있다. 하나라도 빠진 토큰은 서명이 맞아도 거부한다(만료 없는
# 토큰을 받지 않으려고).
@pytest.mark.parametrize("missing", ["exp", "iat", "sub"])
def test_tokens_missing_a_required_claim_are_rejected(jose_secret, missing):
    payload = {"sub": str(JOSE_SUBJECT), "type": "access", "iat": JOSE_IAT, "exp": JOSE_EXP}
    del payload[missing]
    with pytest.raises(InvalidTokenError):
        decode_token(_signed(payload), TokenType.ACCESS)


# 서명이 맞아도 sub가 UUID 모양이 아니면 InvalidTokenError(라우터에서 401)다. 예전에는 uuid.UUID가 낸
# ValueError가 그대로 새어 나가 401 대신 500이 됐다. 이 앱은 sub에 늘 str(uuid)를 넣으므로 이런 토큰은
# 비밀키를 아는 쪽이 직접 만든 것뿐이지만, 비밀키가 공개 예시 값인 서버에서는 누구나 만들 수 있다. 빈 문자열은
# PyJWT의 필수 클레임 검사(값이 None인지만 봄)를 통과하므로 여기까지 온다. 문자열이 아닌 sub(정수 12345)는
# PyJWT가 jwt.decode에서 먼저 거부한다(InvalidSubjectError). 그 경우는 고치기 전에도 통과하던 회귀 방지다.
@pytest.mark.parametrize("subject", ["not-a-uuid", "12345", "", 12345])
def test_a_signed_token_whose_subject_is_not_a_uuid_is_rejected(jose_secret, subject):
    payload = {"sub": subject, "type": "access", "iat": JOSE_IAT, "exp": JOSE_EXP}
    with pytest.raises(InvalidTokenError):
        decode_token(_signed(payload), TokenType.ACCESS)


# 감사 로그의 이메일 지문은 '앞뒤 공백을 빼고 소문자로 바꾼 주소의 UTF-8 sha256 16진수 앞 8자'다. 운영자가
# 손으로 같은 값을 만들어 로그를 찾을 수 있게 공식을 고정한다. 대소문자·공백만 다른 입력은 같은 지문이 되고,
# JSON의 "\ud800" 같은 고립 서로게이트가 든 문자열에서도 예외를 내지 않는다(로그 한 줄 때문에 요청이 500이
# 되면 안 됨).
def test_email_fingerprint_is_the_documented_sha256_prefix():
    expected = hashlib.sha256(b"alice@example.com").hexdigest()[:8]

    assert email_fingerprint("alice@example.com") == expected
    assert email_fingerprint("  Alice@Example.COM ") == expected
    assert email_fingerprint("bob@example.com") != expected
    assert len(email_fingerprint("\ud800@example.com")) == 8


# --- 감사 로그: 관리자 토큰 검사 (app/dependencies.py의 require_admin_token) ---


# 의존성 함수를 HTTP 없이 바로 부를 때 넘길 요청. 감사 로그가 읽는 메서드·경로·클라이언트 주소만 채운다.
# 203.0.113.0/24는 문서용 예시 주소 대역(RFC 5737)이다.
def _admin_request(client: tuple[str, int] | None = ("203.0.113.7", 50123)) -> Request:
    return Request(
        {
            "type": "http",
            "method": "POST",
            "path": "/admin/documents/ingest",
            "query_string": b"",
            "headers": [],
            "client": client,
        }
    )


# 관리자 토큰만 정한 설정. 비밀키는 경고가 나지 않는 길이로 둔다.
def _admin_settings(token: str) -> Settings:
    return Settings(database_url="x", jwt_secret_key="k" * 48, admin_ingest_token=token, _env_file=None)


# 이 모듈 로거의 기록만 고른다(다른 로거의 기록이 섞여도 단언이 흔들리지 않게).
def _dependency_records(caplog) -> list[logging.LogRecord]:
    return [record for record in caplog.records if record.name == "app.dependencies"]


# 거부된 관리자 토큰은 WARNING 한 줄로 남고, 꺼져 있어서인지(설정이 비었거나 공개 예시 값) 값이 틀려서인지를
# reason으로 구분한다. 보낸 헤더 값과 설정된 토큰은 로그 어디에도 없어야 한다.
@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("configured", "sent", "reason"),
    [
        ("", "guess-from-the-client", "disabled"),
        ("change-me-admin-token", "change-me-admin-token", "disabled"),
        ("a-real-secret-token", "a-wrong-guess", "mismatch"),
    ],
)
async def test_a_rejected_admin_token_is_logged_with_its_reason_but_not_its_value(
    caplog, configured, sent, reason
):
    settings = _admin_settings(configured)
    with caplog.at_level(logging.INFO, logger="app.dependencies"):
        with pytest.raises(HTTPException) as raised:
            await require_admin_token(_admin_request(), x_admin_token=sent, settings=settings)

    assert raised.value.status_code == 403
    assert [(record.levelno, record.getMessage()) for record in _dependency_records(caplog)] == [
        (
            logging.WARNING,
            f"admin token rejected reason={reason} on POST /admin/documents/ingest client=203.0.113.7",
        )
    ]
    assert sent not in caplog.text
    if configured:
        assert configured not in caplog.text


# 맞는 관리자 토큰도 INFO 한 줄로 남긴다(적재는 문서 삭제까지 하는 관리자 작업이라 누가 돌렸는지가 감사 대상).
# 토큰 값은 남기지 않는다. 클라이언트 주소를 모르면(request.client가 None) '-'로 적는다.
@pytest.mark.asyncio
async def test_an_accepted_admin_token_is_logged_without_its_value(caplog):
    with caplog.at_level(logging.INFO, logger="app.dependencies"):
        await require_admin_token(
            _admin_request(client=None),
            x_admin_token="a-real-secret-token",
            settings=_admin_settings("a-real-secret-token"),
        )

    assert [(record.levelno, record.getMessage()) for record in _dependency_records(caplog)] == [
        (logging.INFO, "admin token accepted on POST /admin/documents/ingest client=-")
    ]
    assert "a-real-secret-token" not in caplog.text


# 비밀키 검사: 빈 값, 공개 예시 값, 32바이트 미만은 문제로 보고, 충분히 긴 무작위 값은 통과한다.
def test_jwt_secret_problem_flags_empty_public_and_short_secrets():
    assert "change-me-to-a-random-secret" in PUBLIC_EXAMPLE_JWT_SECRETS
    assert jwt_secret_problem("") is not None
    assert jwt_secret_problem("change-me-to-a-random-secret") is not None
    assert jwt_secret_problem("  change-me-to-a-random-secret  ") is not None
    assert jwt_secret_problem("x" * (MIN_JWT_SECRET_BYTES - 1)) is not None
    assert jwt_secret_problem("x" * MIN_JWT_SECRET_BYTES) is None


# CI 워크플로(.github/workflows/ci.yml)의 JWT_SECRET_KEY도 저장소에 공개된 값이다. 32바이트를 넘어 길이
# 검사만으로는 걸리지 않으므로 공개 값 목록에 있어야 한다. 값은 워크플로 파일에서 직접 읽어, CI 값을 바꾸면
# 이 테스트가 목록도 고치라고 알린다. CI는 APP_ENV를 두지 않아(development) 경고만 나고 테스트는 그대로 돈다.
CI_WORKFLOW = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "ci.yml"


def test_the_ci_workflow_secret_counts_as_a_public_value():
    secrets_in_ci = re.findall(r"JWT_SECRET_KEY:\s*(\S+)", CI_WORKFLOW.read_text(encoding="utf-8"))

    assert secrets_in_ci
    for secret in secrets_in_ci:
        assert len(secret.encode("utf-8")) >= MIN_JWT_SECRET_BYTES  # 길이만으로는 걸리지 않는 값이다
        assert secret in PUBLIC_EXAMPLE_JWT_SECRETS
        assert jwt_secret_problem(secret) is not None
        with pytest.raises(ValidationError, match="JWT_SECRET_KEY"):
            Settings(database_url="x", jwt_secret_key=secret, app_env="production", _env_file=None)


# 비밀키 최소 길이는 서명 알고리즘의 해시 출력 길이다. RFC 7518 3.2절의 기준이고, PyJWT가
# InsecureKeyLengthWarning을 내는 기준(hash_alg().digest_size)과도 같다. 그래서 HS512를 고르면 HS256에
# 충분한 32바이트 키도 약한 키로 보고, production이면 시작하지 않는다. 기대값은 앱의 표가 아니라 PyJWT에서
# 읽는다(두 기준이 어긋나면 이 테스트가 잡는다).
@pytest.mark.parametrize("algorithm", ["HS256", "HS384", "HS512"])
def test_the_secret_must_be_as_long_as_the_hash_of_the_signing_algorithm(algorithm):
    minimum = get_default_algorithms()[algorithm].hash_alg().digest_size
    short, enough = "x" * (minimum - 1), "x" * minimum

    assert jwt_secret_problem(short, algorithm) is not None
    assert jwt_secret_problem(enough, algorithm) is None
    production = {"database_url": "x", "jwt_algorithm": algorithm, "app_env": "production", "_env_file": None}
    with pytest.raises(ValidationError, match="JWT_SECRET_KEY"):
        Settings(jwt_secret_key=short, **production)
    assert Settings(jwt_secret_key=enough, **production).jwt_algorithm == algorithm


# 시작 경고도 고른 알고리즘의 최소 길이를 알려 준다(HS512면 64바이트).
def test_the_startup_warning_names_the_minimum_for_the_signing_algorithm(caplog):
    settings = Settings(database_url="x", jwt_secret_key="k" * 48, jwt_algorithm="HS512", _env_file=None)

    with caplog.at_level(logging.WARNING, logger="app.config"):
        assert warn_if_weak_jwt_secret(settings) is True
    assert "64 bytes" in caplog.text


# 기본(APP_ENV=development)에서는 공개 예시 비밀키로도 설정이 만들어진다. 지금 로컬 실행을 깨지 않으려는
# 것이다. 대신 시작할 때 큰 경고를 남긴다.
def test_development_mode_accepts_the_public_secret_but_warns(caplog):
    settings = Settings(database_url="x", jwt_secret_key="change-me-to-a-random-secret", _env_file=None)
    assert settings.app_env == "development"
    with caplog.at_level(logging.WARNING, logger="app.config"):
        assert warn_if_weak_jwt_secret(settings) is True
    assert "JWT_SECRET_KEY" in caplog.text


# 비밀키가 괜찮으면 경고하지 않는다.
def test_a_strong_secret_does_not_warn(caplog):
    settings = Settings(database_url="x", jwt_secret_key="k" * 48, _env_file=None)
    with caplog.at_level(logging.WARNING, logger="app.config"):
        assert warn_if_weak_jwt_secret(settings) is False
    assert caplog.text == ""


# APP_ENV=production이면 약한 비밀키로는 설정 자체가 만들어지지 않아 앱이 시작하지 않는다.
@pytest.mark.parametrize("secret", ["", "change-me-to-a-random-secret", "short-secret"])
def test_production_mode_refuses_a_weak_secret(secret):
    with pytest.raises(ValidationError, match="JWT_SECRET_KEY"):
        Settings(database_url="x", jwt_secret_key=secret, app_env="production", _env_file=None)


def test_production_mode_accepts_a_strong_secret():
    settings = Settings(database_url="x", jwt_secret_key="k" * 48, app_env="production", _env_file=None)
    assert settings.app_env == "production"

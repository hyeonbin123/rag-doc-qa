"""JWT 발급·검증(PyJWT)과 JWT 비밀키 검사를 고정한다.

python-jose(3.5.0, 고친 판이 없는 권고 GHSA-3qf3-8w2g-rqmx)를 PyJWT로 바꾸면서 넣은 테스트다. 바꾸기 전에
python-jose로 만든 토큰을 그대로 적어 두고, 바꾼 뒤에도 같은 토큰이 풀리고 같은 클레임이면 같은 문자열이
나오는지 본다. 이미 발급된 토큰(접근 30분, 갱신 7일)이 교체 뒤에도 그대로 쓰여야 하기 때문이다.
"""

# [테스트 묶음] app/services/security.py의 토큰 함수·이메일 지문, app/config.py의 JWT 비밀키 검사, 관리자 토큰
# 검사(app/dependencies.py의 require_admin_token)가 남기는 감사 로그, 관리자 적재 토큰의 강도
# 검사(app/config.py). DB가 필요 없다.
# [왜 중요한가]
# - 토큰 형식이 바뀌면 배포 순간 모든 사용자가 로그아웃된다. 머리글·클레임·서명이 바이트 단위로 같아야 한다.
# - 알고리즘을 HS256 하나로 고정해야 'alg: none'이나 다른 알고리즘을 주장하는 토큰을 받지 않는다.
# - 서명이 맞아도 sub가 UUID가 아닌 토큰은 500이 아니라 401(InvalidTokenError)이어야 한다.
# - 공개 예시 비밀키(.env.example 값)로 서명하면 누구나 토큰을 만들 수 있다. 기본은 경고,
#   APP_ENV=production이면 시작 거부다. CI 워크플로의 비밀키도 저장소에 공개된 값이라 같은 취급을 한다.
# - 비밀키 최소 길이는 서명 알고리즘의 해시 출력 길이다(HS256 32, HS384 48, HS512 64바이트).
# - 관리자 적재 토큰도 켜져 있다면 32바이트 이상이어야 한다. 짧으면 기본(development)은 경고, production은
#   시작 거부이고, 비어 있는(꺼진) 값은 그대로 받는다. 오류·경고 문구에는 토큰 값이 실리지 않는다.
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

from app import dependencies
from app.config import (
    MIN_ADMIN_INGEST_TOKEN_BYTES,
    MIN_JWT_SECRET_BYTES,
    PLACEHOLDER_ADMIN_TOKENS,
    PUBLIC_EXAMPLE_JWT_SECRETS,
    Settings,
    admin_ingest_token_problem,
    jwt_secret_problem,
    warn_if_weak_admin_ingest_token,
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
        ("  change-me-admin-token ", "  change-me-admin-token ", "disabled"),
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


# 공백뿐인 설정도 '꺼짐'이다: 시작 검사(app/config.py)가 앞뒤 공백을 떼고 빈 값으로 보아 조용히 넘기므로, 요청
# 검사가 공백을 떼지 않고 견주면 그 공백이 그대로 토큰이 되어 같은 공백을 보낸 요청이 통과한다. 위 표의 공백
# 붙은 예시 값과 같은 약속을 본다. 로그에 값이 없다는 것을 글자 찾기로 볼 수 없어(로그 줄에도 공백이 있다)
# 표에 넣지 않고 따로 둔다.
@pytest.mark.asyncio
@pytest.mark.parametrize("configured", ["   ", " \t "])
async def test_a_whitespace_only_admin_token_is_switched_off(caplog, configured):
    settings = _admin_settings(configured)
    with caplog.at_level(logging.INFO, logger="app.dependencies"):
        with pytest.raises(HTTPException) as raised:
            await require_admin_token(_admin_request(), x_admin_token=configured, settings=settings)

    assert raised.value.status_code == 403
    assert [record.getMessage() for record in _dependency_records(caplog)] == [
        "admin token rejected reason=disabled on POST /admin/documents/ingest client=203.0.113.7"
    ]


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


# --- 관리자 적재 토큰의 강도 (app/config.py의 admin_ingest_token_problem, 시작 검사, 시작 경고) ---
#
# 관리자 적재 API는 GitHub에서 문서를 받아 DB에 쓰고 사라진 문서를 지우며, 실패 횟수를 제한하지 않는다.
# 그래서 켜져 있는 토큰이 추측하기 쉬우면 같은 네트워크의 로그인하지 않은 사용자가 맞힐 수 있다. JWT
# 비밀키와 같은 방식으로, 비어 있지 않은데 32바이트 미만이면 production은 시작을 거부하고 development는
# 시작할 때 경고한다. 비어 있는 값(기능 꺼짐)과 옛 공개 예시 값(요청 검사도 꺼진 것으로 봄)은 문제로 보지
# 않는다.

# 32바이트 이상인, 뻔히 가짜인 토큰. 실제 배포에서 쓰는 값이 아니다. 길이는 안내하는
# secrets.token_urlsafe(32)의 결과(문자 43개)와 같다.
STRONG_ADMIN_TOKEN = "fake-admin-token-for-tests-0123456789abcdef"
# 32바이트 미만(20바이트)인 짧은 토큰. 오류·경고 문구에 값이 실렸는지 찾을 수 있게, 다른 글에는 나올 리
# 없는 표식을 넣었다.
WEAK_ADMIN_TOKEN = "weak-marker-not-real"


# 관리자 토큰과 실행 환경만 정한 설정. 비밀키는 경고가 나지 않는 길이로 두고, 저장소의 .env는 읽지 않는다.
def _settings(app_env: str = "development", admin_token: str = "") -> Settings:
    return Settings(
        database_url="x",
        jwt_secret_key="k" * 48,
        app_env=app_env,
        admin_ingest_token=admin_token,
        _env_file=None,
    )


# 켜져 있는데 32바이트 미만인 값만 문제로 본다. 비어 있는 값, 공백뿐인 값, 옛 공개 예시 값은 관리자 적재
# API가 꺼진 상태(require_admin_token이 어떤 헤더가 와도 403)라 토큰이 지킬 것이 없어서 문제가 아니다.
def test_admin_ingest_token_problem_flags_only_short_values_that_switch_the_api_on():
    assert MIN_ADMIN_INGEST_TOKEN_BYTES == 32
    for switched_off in ("", "   ", "change-me-admin-token", "  change-me-admin-token  "):
        assert admin_ingest_token_problem(switched_off) is None, repr(switched_off)
    for weak in ("a", "admin", "password", WEAK_ADMIN_TOKEN, "x" * (MIN_ADMIN_INGEST_TOKEN_BYTES - 1)):
        assert admin_ingest_token_problem(weak) is not None, weak
    assert admin_ingest_token_problem("x" * MIN_ADMIN_INGEST_TOKEN_BYTES) is None
    assert admin_ingest_token_problem(STRONG_ADMIN_TOKEN) is None


# 길이는 UTF-8 바이트 수로, 앞뒤 공백을 뗀 값으로 센다. 공백으로 길이만 채운 짧은 값이 검사를 피하지
# 못하게 하고 (JWT 비밀키 검사가 공개 값을 뗀 값으로 비교하는 것과 같은 생각), 한글처럼 한 글자가 여러
# 바이트인 값은 바이트로 센다(JWT 비밀키 검사도 바이트로 센다).
def test_admin_ingest_token_length_counts_bytes_without_surrounding_whitespace():
    assert admin_ingest_token_problem("x" * 31 + " ") is not None
    assert admin_ingest_token_problem(" " * 5 + "x" * 31) is not None
    assert admin_ingest_token_problem(" " + "x" * 32 + " ") is None
    assert admin_ingest_token_problem("가" * 10) is not None  # 30바이트
    assert admin_ingest_token_problem("가" * 11) is None  # 33바이트


# 문제 문장은 시작 오류와 경고 로그에 그대로 나가므로 토큰 값을 담지 않는다. 대신 어느 설정이 문제인지,
# 최소 길이, 고치는 길(충분히 긴 값을 두거나 비워 기능을 끈다)을 알려 준다.
def test_the_admin_token_problem_names_the_setting_but_not_the_value():
    problem = admin_ingest_token_problem(WEAK_ADMIN_TOKEN)

    assert problem is not None
    assert "ADMIN_INGEST_TOKEN" in problem
    assert str(MIN_ADMIN_INGEST_TOKEN_BYTES) in problem
    assert "empty" in problem
    assert WEAK_ADMIN_TOKEN not in problem


# APP_ENV=production이면 짧은 관리자 토큰으로는 설정 자체가 만들어지지 않아 앱이 시작하지 않는다(JWT
# 비밀키와 같다). 앞뒤 공백으로 32바이트를 채운 값도 마찬가지다.
@pytest.mark.parametrize("token", ["a", "admin", "password", WEAK_ADMIN_TOKEN, "x" * 31, "x" * 31 + " "])
def test_production_mode_refuses_a_short_admin_token(token):
    with pytest.raises(ValidationError, match="ADMIN_INGEST_TOKEN"):
        _settings("production", token)


# 시작을 거부하는 오류 문구에 토큰 값이 실리면 안 된다. pydantic은 모델 검증기의 오류 문자열에 검증에
# 넘어간 입력 전체의 앞뒤 일부(input_value)를 붙이는데, 환경 변수로 설정을 줄 때 admin_ingest_token은
# 입력의 마지막 키라 그 값이 그대로 찍혔다. Settings의 hide_input_in_errors가 이를 막는다. 생성자 인자로
# 주는 경우와 컨테이너처럼 환경 변수로 주는 경우를 모두 본다.
def test_the_production_refusal_does_not_print_the_admin_token(monkeypatch):
    with pytest.raises(ValidationError) as from_arguments:
        _settings("production", WEAK_ADMIN_TOKEN)
    assert "ADMIN_INGEST_TOKEN" in str(from_arguments.value)
    assert WEAK_ADMIN_TOKEN not in str(from_arguments.value)

    monkeypatch.setenv("DATABASE_URL", "x")
    monkeypatch.setenv("JWT_SECRET_KEY", "k" * 48)
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("ADMIN_INGEST_TOKEN", WEAK_ADMIN_TOKEN)
    with pytest.raises(ValidationError) as from_environment:
        Settings(_env_file=None)
    assert "ADMIN_INGEST_TOKEN" in str(from_environment.value)
    assert WEAK_ADMIN_TOKEN not in str(from_environment.value)


# 약한 JWT 비밀키 때문에 시작을 거부하는 오류에도 (켜져 있는) 관리자 토큰이 실리면 안 된다. 같은 이유로
# 예전에는 이 오류 문자열 끝에 입력의 마지막 키인 관리자 토큰의 끝부분이 찍혔다. 오류에는 입력의 앞뒤 25자
# 정도만 실리므로, 긴 토큰은 끝 12자가 없는지로 본다.
def test_the_jwt_refusal_does_not_print_the_admin_token(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "x")
    monkeypatch.setenv("JWT_SECRET_KEY", "short-secret")
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("ADMIN_INGEST_TOKEN", STRONG_ADMIN_TOKEN)

    with pytest.raises(ValidationError, match="JWT_SECRET_KEY") as excinfo:
        Settings(_env_file=None)

    assert STRONG_ADMIN_TOKEN[-12:] not in str(excinfo.value)


# production에서도 충분히 긴 토큰, 정확히 32바이트인 토큰(경계), 비어 있는 값(기능 꺼짐), 공백뿐인 값, 옛
# 공개 예시 값은 설정이 만들어진다. 뒤의 셋은 관리자 적재 API가 꺼진 채 시작하는 것이라 시작을 막지
# 않는다(전에도 시작했다).
@pytest.mark.parametrize("token", [STRONG_ADMIN_TOKEN, "x" * 32, "", "   ", "change-me-admin-token"])
def test_production_mode_accepts_a_long_or_switched_off_admin_token(token):
    settings = _settings("production", token)

    assert settings.app_env == "production"
    assert settings.admin_ingest_token == token


# 기본(APP_ENV=development)에서는 짧은 토큰으로도 설정이 만들어지고(지금 로컬 실행을 깨지 않으려는 것),
# 시작할 때 경고를 남긴다. 경고에는 설정 이름과 최소 길이가 있고 토큰 값은 없다.
def test_development_mode_accepts_a_short_admin_token_but_warns(caplog):
    settings = _settings(admin_token=WEAK_ADMIN_TOKEN)

    assert settings.app_env == "development"
    with caplog.at_level(logging.WARNING, logger="app.config"):
        assert warn_if_weak_admin_ingest_token(settings) is True
    assert "ADMIN_INGEST_TOKEN" in caplog.text
    assert "32 bytes" in caplog.text
    assert WEAK_ADMIN_TOKEN not in caplog.text


# 충분히 긴 토큰, 비어 있는 값, 옛 공개 예시 값에는 경고하지 않는다(토큰이 충분하거나 기능이 꺼져 있다).
@pytest.mark.parametrize("token", [STRONG_ADMIN_TOKEN, "", "change-me-admin-token"])
def test_a_long_or_switched_off_admin_token_does_not_warn(caplog, token):
    settings = _settings(admin_token=token)

    with caplog.at_level(logging.WARNING, logger="app.config"):
        assert warn_if_weak_admin_ingest_token(settings) is False
    assert caplog.text == ""


# 시작 검사(app/config.py)와 요청 검사(app/dependencies.py)가 '꺼짐'으로 보는 값의 집합은 하나다. 두 곳에
# 따로 두면 한쪽만 고쳐져, 시작 검사는 '꺼짐'으로 보고 넘기는데 요청 검사는 그 값을 토큰으로 받아 켜지는
# 틈이 생길 수 있다.
def test_the_start_check_and_the_request_check_share_the_placeholder_values():
    assert dependencies.PLACEHOLDER_ADMIN_TOKENS is PLACEHOLDER_ADMIN_TOKENS
    assert {"", "change-me-admin-token"} <= PLACEHOLDER_ADMIN_TOKENS

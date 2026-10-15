"""JWT 발급·검증(PyJWT)과 JWT 비밀키 검사를 고정한다.

python-jose(3.5.0, 고친 판이 없는 권고 GHSA-3qf3-8w2g-rqmx)를 PyJWT로 바꾸면서 넣은 테스트다. 바꾸기 전에
python-jose로 만든 토큰을 그대로 적어 두고, 바꾼 뒤에도 같은 토큰이 풀리고 같은 클레임이면 같은 문자열이
나오는지 본다. 이미 발급된 토큰(접근 30분, 갱신 7일)이 교체 뒤에도 그대로 쓰여야 하기 때문이다.
"""

# [테스트 묶음] app/services/security.py의 토큰 함수와 app/config.py의 JWT 비밀키 검사. DB가 필요 없다.
# [왜 중요한가]
# - 토큰 형식이 바뀌면 배포 순간 모든 사용자가 로그아웃된다. 머리글·클레임·서명이 바이트 단위로 같아야 한다.
# - 알고리즘을 HS256 하나로 고정해야 'alg: none'이나 다른 알고리즘을 주장하는 토큰을 받지 않는다.
# - 공개 예시 비밀키(.env.example 값)로 서명하면 누구나 토큰을 만들 수 있다. 기본은 경고,
#   APP_ENV=production이면
#   시작 거부다.

import logging
import uuid
from datetime import UTC, datetime, timedelta

# jwt: PyJWT. 테스트에서 일부러 잘못된 토큰(다른 알고리즘, 만료, 클레임 빠짐)을 만들 때만 직접 쓴다.
import jwt
import pytest
from pydantic import ValidationError

from app.config import (
    MIN_JWT_SECRET_BYTES,
    PUBLIC_EXAMPLE_JWT_SECRETS,
    Settings,
    jwt_secret_problem,
    warn_if_weak_jwt_secret,
)
from app.services import security
from app.services.security import InvalidTokenError, TokenType, decode_token

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


# 비밀키 검사: 빈 값, 공개 예시 값, 32바이트 미만은 문제로 보고, 충분히 긴 무작위 값은 통과한다.
def test_jwt_secret_problem_flags_empty_public_and_short_secrets():
    assert "change-me-to-a-random-secret" in PUBLIC_EXAMPLE_JWT_SECRETS
    assert jwt_secret_problem("") is not None
    assert jwt_secret_problem("change-me-to-a-random-secret") is not None
    assert jwt_secret_problem("  change-me-to-a-random-secret  ") is not None
    assert jwt_secret_problem("x" * (MIN_JWT_SECRET_BYTES - 1)) is not None
    assert jwt_secret_problem("x" * MIN_JWT_SECRET_BYTES) is None


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

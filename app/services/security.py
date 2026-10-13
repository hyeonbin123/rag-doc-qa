# [파일 역할] 비밀번호 해시(bcrypt)와 JWT 토큰 발급·검증을 맡는 보안 유틸리티.
# [설계]
# - 비밀번호는 원문을 저장하지 않고 솔트가 들어간 bcrypt 해시만 저장한다.
# - 토큰은 수명이 짧은 접근 토큰과 긴 갱신 토큰 두 종류이고, payload의 type 클레임으로 구분해 서로의 자리에
#   쓰지 못하게 한다.
# [연결] 가입·로그인·갱신(app/routers/auth.py), 요청마다 토큰 확인(app/dependencies.py의 get_current_user),
# 비밀번호 바이트 한도(app/schemas/auth.py)가 이 모듈을 쓴다.

import uuid
from datetime import UTC, datetime, timedelta
from enum import StrEnum

# bcrypt: 일부러 느리게 만든 비밀번호 해시 함수(무차별 대입을 비싸게 만든다). python-jose의 jwt: JWT
# 서명·검증.
import bcrypt
from jose import JWTError, jwt

from app.config import get_settings

# 모듈을 import할 때 설정을 읽어 JWT 키·알고리즘·수명을 쓴다.
settings = get_settings()

# bcrypt reads at most 72 bytes of a password, and bcrypt 5 raises on longer input
# instead of truncating it. Registration rejects such passwords (UserRegister); at
# login they cannot match any stored hash. Bytes, not characters: a Korean character
# is 3 bytes in UTF-8.
MAX_PASSWORD_BYTES = 72


# 토큰 종류. 문자열 값이 그대로 JWT payload의 type 클레임에 들어간다.
class TokenType(StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"


# 비밀번호를 bcrypt 해시 문자열로 바꾼다. gensalt()가 매번 새 무작위 솔트를 만들고 그 솔트와 비용 값이 해시
# 문자열 안에 함께 들어가므로, 검증할 때 따로 저장할 것이 없다. CPU를 많이 쓰는 동기 호출이라 라우터는
# 스레드에서 부른다.
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


# 입력 비밀번호가 저장된 해시와 맞는지 확인한다. 72바이트를 넘으면 bcrypt를 부르지 않고 바로 False를 돌려준다.
# bcrypt 5는 긴 입력에 ValueError를 내서 로그인이 500이 됐기 때문이고, 가입 단계에서 그런 비밀번호는 이미
# 거부되므로 맞는 해시가 있을 수 없다. checkpw는 해시 문자열에서 솔트를 꺼내 같은 방식으로 다시 해시해
# 비교한다.
def verify_password(password: str, hashed_password: str) -> bool:
    encoded = password.encode("utf-8")
    if len(encoded) > MAX_PASSWORD_BYTES:
        return False
    return bcrypt.checkpw(encoded, hashed_password.encode("utf-8"))


# JWT를 만든다. sub=사용자 id(문자열), type=토큰 종류, iat=발급 시각, exp=만료 시각. 시각은 시간대가 있는
# UTC로 만들고, python-jose가 숫자 타임스탬프로 바꿔 넣는다. 설정의 비밀키·알고리즘(HS256)으로 서명한다.
def _create_token(subject: uuid.UUID, token_type: TokenType, expires_delta: timedelta) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": str(subject),
        "type": token_type.value,
        "iat": now,
        "exp": now + expires_delta,
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


# 접근 토큰: API 호출마다 Authorization 헤더에 싣는 짧은 수명(기본 30분) 토큰.
def create_access_token(user_id: uuid.UUID) -> str:
    return _create_token(
        user_id, TokenType.ACCESS, timedelta(minutes=settings.access_token_expire_minutes)
    )


# 갱신 토큰: /auth/refresh에서 새 접근 토큰을 받을 때만 쓰는 긴 수명(기본 7일) 토큰.
def create_refresh_token(user_id: uuid.UUID) -> str:
    return _create_token(
        user_id, TokenType.REFRESH, timedelta(days=settings.refresh_token_expire_days)
    )


# 토큰 문제(서명·만료 오류, 종류 불일치, sub 없음)를 하나로 묶은 예외. 호출한 쪽은 이것 하나만 잡아 401로
# 바꾼다.
class InvalidTokenError(Exception):
    pass


# 토큰을 검증하고 사용자 id를 돌려준다. 순서대로 확인한다.
# 1) 서명과 만료: jwt.decode가 비밀키로 서명을 확인하고 exp가 지났으면 거부한다. algorithms를 설정값 하나로
#    고정해, 토큰 머리글이 다른 알고리즘을 주장해도 받아들이지 않는다.
# 2) 종류: 기대한 type(access/refresh)이 아니면 거부한다.
# 3) sub가 있어야 하고 UUID로 바꾼다.
def decode_token(token: str, expected_type: TokenType) -> uuid.UUID:
    try:
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
    except JWTError as exc:
        raise InvalidTokenError("could not validate token") from exc

    if payload.get("type") != expected_type.value:
        raise InvalidTokenError(f"expected a {expected_type.value} token")

    subject = payload.get("sub")
    if subject is None:
        raise InvalidTokenError("token has no subject")

    return uuid.UUID(subject)

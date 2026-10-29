# [파일 역할] 비밀번호 해시(bcrypt)와 JWT 토큰 발급·검증, 감사 로그용 이메일 지문을 맡는 보안 유틸리티.
# [설계]
# - 비밀번호는 원문을 저장하지 않고 솔트가 들어간 bcrypt 해시만 저장한다.
# - 토큰은 수명이 짧은 접근 토큰과 긴 갱신 토큰 두 종류이고, payload의 type 클레임으로 구분해 서로의 자리에
#   쓰지 못하게 한다.
# - 감사 로그에는 이메일 원문 대신 지문(email_fingerprint)만 남긴다.
# [연결] 가입·로그인·갱신(app/routers/auth.py), 요청마다 토큰 확인(app/dependencies.py의 get_current_user),
# 비밀번호 바이트 한도(app/schemas/auth.py)가 이 모듈을 쓴다.

import hashlib
import uuid
from datetime import UTC, datetime, timedelta
from enum import StrEnum

# bcrypt: 일부러 느리게 만든 비밀번호 해시 함수(무차별 대입을 비싸게 만든다). jwt: PyJWT, JWT 서명·검증.
# 2026-10까지는 python-jose를 썼다. python-jose 3.5.0에 고친 판이 없는 보안 권고(GHSA-3qf3-8w2g-rqmx)가 붙고
# 의존하는 ecdsa도 고칠 계획이 없는 권고가 있어 PyJWT로 바꿨다. 이 앱은 HS256 대칭키만 쓰고 algorithms를
# 고정해 그 권고의 공격 경로는 없었지만, 의존성 검사(CI의 pip-audit)에 늘 걸리기 때문이다. 같은 클레임이면
# 두 라이브러리가 바이트 단위로 같은 토큰을 만들어(머리글 키 정렬, 숫자 타임스탬프, 같은 JSON 구분자) 이미
# 발급된 토큰도 그대로 풀린다(tests/test_security.py).
import bcrypt
import jwt

from app.config import get_settings

# 모듈을 import할 때 설정을 읽어 JWT 키·알고리즘·수명을 쓴다.
settings = get_settings()

# bcrypt는 비밀번호를 최대 72바이트까지만 읽고, bcrypt 5는 더 긴 입력을 잘라 쓰는 대신 예외를 낸다. 가입은
# 이런 비밀번호를 거부하고(UserRegister), 로그인에서는 저장된 어떤 해시와도 맞을 수 없다. 글자 수가 아니라
# 바이트 수다: 한글 한 글자는 UTF-8로 3바이트다.
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
# UTC로 만들고, PyJWT가 숫자 타임스탬프(초)로 바꿔 넣는다. 설정의 비밀키·알고리즘(HS256)으로 서명한다.
# now는 테스트가 발급 시각을 고정할 때만 넘긴다(python-jose 토큰과 바이트 단위로 같은지 보는 테스트). 앱은
# 넘기지 않아 지금 시각을 쓴다.
def _create_token(
    subject: uuid.UUID, token_type: TokenType, expires_delta: timedelta, *, now: datetime | None = None
) -> str:
    now = now or datetime.now(UTC)
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


# 토큰 문제(서명·만료 오류, 종류 불일치, sub 없음, sub가 UUID가 아님)를 하나로 묶은 예외. 호출한 쪽은 이것
# 하나만 잡아 401로 바꾼다. 메시지는 아래 decode_token의 고정 영어 문구뿐이고 토큰 내용을 담지 않는다. 갱신
# 거부 감사 로그(app/routers/auth.py)가 이 메시지를 그대로 적기 때문에, 새 메시지에도 토큰 값을 넣지 않는다.
class InvalidTokenError(Exception):
    pass


# decode_token이 요구하는 클레임. 이 앱이 발급하는 토큰에는 늘 들어 있다. 특히 exp가 없는 토큰(만료되지 않는
# 토큰)은 서명이 맞아도 받지 않는다. python-jose는 exp가 있을 때만 확인했으므로 이 점은 더 엄격해졌다.
REQUIRED_CLAIMS = ["exp", "iat", "sub"]


# 토큰을 검증하고 사용자 id를 돌려준다. 순서대로 확인한다.
# 1) 서명·만료·필수 클레임: jwt.decode가 비밀키로 서명을 확인하고, exp가 지났거나 iat가 미래이거나 위 필수
#    클레임이 빠졌으면 거부한다. algorithms를 설정값 하나(HS256)로 고정해, 토큰 머리글이 다른 알고리즘('none',
#    HS512 등)을 주장해도 받아들이지 않는다.
# 2) 종류: 기대한 type(access/refresh)이 아니면 거부한다.
# 3) sub가 있어야 하고 UUID로 바꾼다. UUID 모양이 아니면(서명은 맞지만 이 앱이 발급하지 않는 형식) 거부한다.
#    예전에는 uuid.UUID의 ValueError가 그대로 새어 나가 401 대신 500이 됐다. 이런 토큰은 비밀키를 아는 쪽만
#    만들 수 있지만, 비밀키가 공개 예시 값인 서버에서는 누구나 만들 수 있다. 문자열이 아닌 sub(숫자·목록 등)는
#    1)의 jwt.decode가 InvalidSubjectError로 먼저 거부하므로(설치된 PyJWT 2.15.1의 _validate_sub, 정수 sub로
#    tests/test_security.py가 고정) 여기에는 문자열만 온다. 빈 문자열은 필수 클레임 검사(값이 None인지만
#    봄)를 통과해 여기서 걸린다.
# PyJWT의 모든 검증 예외는 jwt.PyJWTError를 상속한다. 이름이 같은 jwt.InvalidTokenError도 그 하위
# 클래스지만, 이 파일에는 아래 앱 자체의 InvalidTokenError가 있으므로 헷갈리지 않게 상위 클래스로 잡는다.
def decode_token(token: str, expected_type: TokenType) -> uuid.UUID:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
            options={"require": REQUIRED_CLAIMS},
        )
    except jwt.PyJWTError as exc:
        raise InvalidTokenError("could not validate token") from exc

    if payload.get("type") != expected_type.value:
        raise InvalidTokenError(f"expected a {expected_type.value} token")

    subject = payload.get("sub")
    if subject is None:
        raise InvalidTokenError("token has no subject")

    try:
        return uuid.UUID(subject)
    except ValueError as exc:
        raise InvalidTokenError("token subject is not a UUID") from exc


# 감사 로그(app/routers/auth.py)에 이메일 원문 대신 남기는 지문의 길이(sha256 16진수 앞 글자 수). 8자는
# 32비트라 주소 1만 개 사이에서 어느 둘이 우연히 겹칠 확률이 약 1%이고, 로그 한 줄을 짧게 둔다.
EMAIL_FINGERPRINT_CHARS = 8


# 감사 로그용 이메일 지문: 앞뒤 공백을 빼고 소문자로 바꾼 주소를 UTF-8로 인코딩한 sha256의 16진수 앞 8자.
# - 왜 원문이 아닌가: 로그는 DB보다 넓게 퍼지므로(콘솔, 파일, 로그 수집기) 주소 원문을 남기지 않는다. 같은
#   주소의 시도는 같은 지문이 되므로 '한 주소에 실패가 몇 번 몰렸는지'는 그대로 셀 수 있다.
# - 왜 소문자인가: 로그인은 입력한 철자로, 가입은 EmailStr이 정규화한 철자(도메인 소문자)로 들어오므로
#   대소문자만 다른 철자를 한 지문으로 묶는다. 운영자는 같은 공식으로 손으로 계산해 로그를 찾을 수 있다:
#   python -c "import hashlib; print(hashlib.sha256(b'alice@example.com').hexdigest()[:8])"
# - 주의: 익명화가 아니라 가명화다. 후보 주소를 아는 사람은 같은 계산으로 그 주소가 로그에 있는지 확인할 수
#   있으므로 로그도 민감 자료로 다룬다. 솔트나 비밀키를 섞지 않은 것은 운영자가 키 없이 계산할 수 있게 하려는
#   선택이다.
# - surrogatepass: JSON 본문의 "\ud800" 같은 고립 서로게이트가 든 문자열도 예외 없이 바이트로 바꾼다. 로그 한
#   줄 때문에 요청이 500이 되면 안 된다.
def email_fingerprint(email: str) -> str:
    normalized = email.strip().lower().encode("utf-8", "surrogatepass")
    return hashlib.sha256(normalized).hexdigest()[:EMAIL_FINGERPRINT_CHARS]

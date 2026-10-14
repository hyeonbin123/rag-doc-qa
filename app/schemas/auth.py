# [파일 역할] 인증 API(/auth/register, /auth/login, /auth/refresh, /auth/me)의 요청·응답 모양을 pydantic
# 모델로 정한다. 비밀번호 규칙(8자 이상, UTF-8 72바이트 이하)과 이메일 정규화 함수도 여기 있다.
# [왜 스키마에서 검사하나] 잘못된 입력을 DB나 bcrypt까지 보내기 전에 FastAPI가 422로 돌려보내게 하려는 것이다.
# 72바이트를 넘는 비밀번호는 bcrypt 5가 ValueError를 내 가입·로그인이 500이 되던 버그가
# 있었다(app/services/security.py 주석).

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, TypeAdapter, field_validator

# bcrypt 입력 한도(72바이트)는 해시를 다루는 보안 모듈 한곳에 두고 가져와, 가입 검증과 로그인 검사가 같은 값을
# 쓰게 한다.
from app.services.security import MAX_PASSWORD_BYTES

# 가입 비밀번호 최소 길이(글자 수). 로그인에는 걸지 않는다.
MIN_PASSWORD_LENGTH = 8

# 모델 필드 밖에서도 EmailStr과 똑같은 검증·정규화를 하려고 만든 어댑터. 모듈을 불러올 때 한 번만 만든다.
_email_adapter = TypeAdapter(EmailStr)


# 가입(UserRegister)이 저장하는 것과 같은 형태로 주소를 바꾼다. 로그인 조회(app/services/users.py의
# find_user_by_email)와 데모 계정 시드(scripts/seed_demo_user.py)가 써서, 가입 때와 다른 대소문자로 도메인을
# 입력해도 같은 계정을 찾게 한다.
def normalize_email(value: str) -> str:
    """UserRegister가 저장하는 형태(EmailStr 형식, 도메인은 소문자)로 주소를 바꿔 돌려준다.

    값이 이메일 주소가 아니면 ValueError(pydantic의 ValidationError)를 낸다.
    """
    return _email_adapter.validate_python(value)


# 가입 요청 본문. EmailStr이 주소 형식을 검사하고 정규화하며, 어기면 422가 난다. 채팅 화면은 422 응답의 loc
# 마지막 값(필드 이름)으로 이메일 오류와 비밀번호 규칙 위반을 구분해 안내한다(app/web/static/chat.js).
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=MIN_PASSWORD_LENGTH)

    # 글자 수가 아니라 UTF-8 바이트 수로 검사한다. 한글은 한 글자가 3바이트라 25자만 돼도 75바이트로 bcrypt
    # 한도를 넘는다.
    @field_validator("password")
    @classmethod
    def password_fits_bcrypt(cls, value: str) -> str:
        if len(value.encode("utf-8")) > MAX_PASSWORD_BYTES:
            raise ValueError(f"password must be at most {MAX_PASSWORD_BYTES} bytes in UTF-8")
        return value


# 사용자 응답. hashed_password는 필드에 없으므로 응답에 절대 나가지 않는다. from_attributes=True로 ORM User
# 객체를 그대로 response_model에 넘길 수 있다.
class UserOut(BaseModel):
    id: uuid.UUID
    email: EmailStr
    created_at: datetime

    model_config = {"from_attributes": True}


# 로그인 응답: 짧은 접근 토큰과 긴 갱신 토큰. token_type="bearer"는 OAuth2 응답 규약이라 Swagger UI의
# Authorize가 그대로 쓸 수 있다.
class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# /auth/refresh 응답: 새 접근 토큰만 돌려준다(갱신 토큰은 그대로 재사용).
class AccessToken(BaseModel):
    access_token: str
    token_type: str = "bearer"


# /auth/refresh 요청 본문.
class RefreshRequest(BaseModel):
    refresh_token: str

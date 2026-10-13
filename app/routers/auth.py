# [파일 역할] 인증 API 묶음(/auth/register, /auth/login, /auth/refresh, /auth/me). 이메일·비밀번호로 가입하고,
# 로그인하면 JWT 접근·갱신 토큰 쌍을 받는다.
# [설계 포인트]
# - bcrypt 해시·검증은 호출마다 CPU를 약 0.24초 쓰므로 run_in_threadpool로 이벤트 루프 밖에서 돌린다(README
#   '모델 계산은 이벤트 루프 밖에서').
# - 로그인 이메일은 가입 때와 같은 정규화로도 찾는다(app/services/users.py).
# [연결] 토큰 발급·검증은 app/services/security.py, 로그인 사용자 확인 의존성은 app/dependencies.py의
# get_current_user.

# run_in_threadpool: 동기 함수를 Starlette의 기본 스레드 풀에서 실행하고 결과를 await한다.
# OAuth2PasswordRequestForm: OAuth2 password 흐름 규약대로 username·password를 폼 데이터로 받는다(Swagger UI의
# Authorize 버튼이 이 형식으로 보낸다).
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.concurrency import run_in_threadpool
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import AccessToken, RefreshRequest, TokenPair, UserOut, UserRegister
from app.services.security import (
    InvalidTokenError,
    TokenType,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.services.users import find_user_by_email

# 모든 경로 앞에 /auth를 붙이고, Swagger UI에서 auth 묶음으로 보이게 한다.
router = APIRouter(prefix="/auth", tags=["auth"])


# 가입. 성공하면 201과 사용자 정보(UserOut, 해시 없음)를 돌려준다. 이미 있는 주소면 409다. responses에 409를
# 적어 두어 Swagger 문서에 이 응답이 표시되게 한다. 비밀번호 길이·바이트 규칙과 이메일 형식은 UserRegister가
# 먼저 422로 거른다.
@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    responses={status.HTTP_409_CONFLICT: {"description": "Email already registered"}},
)
async def register(payload: UserRegister, db: AsyncSession = Depends(get_db)) -> User:
    # payload.email은 EmailStr이 이미 정규화한 값이라 저장 형태와 같은 문자열로 중복을 확인한다. (동시에 같은
    # 주소로 가입하면 이 확인을 둘 다 통과할 수 있지만, 그때는 email 유일 제약이 두 번째 삽입을 막는다.)
    existing = await db.scalar(select(User).where(User.email == payload.email))
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    # bcrypt costs about a quarter second of CPU per call (cost 12). On the event loop
    # that would stall every other request, so it runs on a worker thread. Not the model
    # pool (run_model): a login shouldn't queue behind embeddings.
    hashed = await run_in_threadpool(hash_password, payload.password)
    user = User(email=payload.email, hashed_password=hashed)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


# 로그인. 폼의 username 칸에 이메일을 넣는다(OAuth2 password 흐름 규약). 성공하면 접근·갱신 토큰 쌍을
# 돌려준다.
@router.post("/login", response_model=TokenPair)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> TokenPair:
    # Registration stores the address as EmailStr normalizes it (domain lower-cased),
    # so the typed username is looked up both as typed and in that form.
    user = await find_user_by_email(db, form_data.username)
    # 사용자가 없을 때와 비밀번호가 틀렸을 때 같은 401 메시지를 돌려줘, 어떤 이메일이 가입돼 있는지 응답
    # 내용으로는 알 수 없게 한다. (없는 이메일이면 bcrypt를 건너뛰므로 응답 시간 차이는 남는다.)
    # 72바이트를 넘는 비밀번호는 verify_password가 bcrypt를 부르지 않고 False를 돌려줘 500 대신 401이 된다.
    if user is None or not await run_in_threadpool(
        verify_password, form_data.password, user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password"
        )

    return TokenPair(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


# 갱신 토큰으로 새 접근 토큰을 받는다. TokenType.REFRESH를 요구하므로 접근 토큰으로는 갱신할 수 없다.
# 서명·만료가 맞아도 사용자가 없거나 비활성이면 401이다. 갱신 토큰 자체는 새로 발급하지 않는다.
@router.post("/refresh", response_model=AccessToken)
async def refresh(payload: RefreshRequest, db: AsyncSession = Depends(get_db)) -> AccessToken:
    try:
        user_id = decode_token(payload.refresh_token, TokenType.REFRESH)
    except InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        ) from exc

    user = await db.get(User, user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    return AccessToken(access_token=create_access_token(user.id))


# 현재 로그인한 사용자 정보. 토큰이 유효한지 확인하는 가장 간단한 엔드포인트다.
@router.get("/me", response_model=UserOut)
async def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user

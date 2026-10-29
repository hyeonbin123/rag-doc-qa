# [파일 역할] 인증 API 묶음(/auth/register, /auth/login, /auth/refresh, /auth/me). 이메일·비밀번호로 가입하고,
# 로그인하면 JWT 접근·갱신 토큰 쌍을 받는다.
# [설계 포인트]
# - bcrypt 해시·검증은 호출마다 CPU를 약 0.24초 쓰므로 run_in_threadpool로 이벤트 루프 밖에서 돌린다(README
#   '모델 계산은 이벤트 루프 밖에서').
# - 로그인 이메일은 가입 때와 같은 정규화로도 찾는다(app/services/users.py).
# - 인증 사건(가입, 로그인 성공·실패, 갱신 거부)을 감사 로그 한 줄로 남긴다. 성공은 INFO, 거부는 WARNING이다.
#   이메일은 지문(app/services/security.py의 email_fingerprint, sha256 앞 8자)으로만, 클라이언트 주소는
#   app/dependencies.py의 client_host로 적고, 비밀번호·토큰 값은 어떤 경우에도 적지 않는다. 예전에는 uvicorn
#   접근 로그(주소·경로·상태 코드)만 남아, 실패가 어느 계정에 몰렸는지와 실패 이유를 뒤에서 알 수 없었다.
# [연결] 토큰 발급·검증은 app/services/security.py, 로그인 사용자 확인 의존성은 app/dependencies.py의
# get_current_user.

import logging

# run_in_threadpool: 동기 함수를 Starlette의 기본 스레드 풀에서 실행하고 결과를 await한다.
# OAuth2PasswordRequestForm: OAuth2 password 흐름 규약대로 username·password를 폼 데이터로 받는다(Swagger UI의
# Authorize 버튼이 이 형식으로 보낸다). Request는 감사 로그의 클라이언트 주소를 읽으려고 받는다.
# IntegrityError: 동시 가입 경쟁에서 늦은 쪽의 삽입이 email 유일 제약에 걸릴 때 commit이 내는 예외.
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.concurrency import run_in_threadpool
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies import client_host, get_current_user
from app.models.user import User
from app.schemas.auth import AccessToken, RefreshRequest, TokenPair, UserOut, UserRegister
from app.services.security import (
    InvalidTokenError,
    TokenType,
    create_access_token,
    create_refresh_token,
    decode_token,
    email_fingerprint,
    hash_password,
    verify_password,
)
from app.services.users import find_user_by_email

# 인증 감사 로그. configure_logging의 형식으로 'app.routers.auth' 이름이 찍힌다. 한 줄에 사건과
# reason·user(UUID)·email(지문)·client를 key=value로 적어 grep으로 셀 수 있게 한다.
logger = logging.getLogger(__name__)

# 모든 경로 앞에 /auth를 붙이고, Swagger UI에서 auth 묶음으로 보이게 한다.
router = APIRouter(prefix="/auth", tags=["auth"])


# 가입. 성공하면 201과 사용자 정보(UserOut, 해시 없음)를 돌려준다. 이미 있는 주소면 409다(같은 주소로 동시에
# 가입한 두 요청 중 늦은 쪽도 409). responses에 409를 적어 두어 Swagger 문서에 이 응답이 표시되게 한다.
# 비밀번호 길이·바이트 규칙과 이메일 형식은 UserRegister가 먼저 422로 거른다.
@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    responses={status.HTTP_409_CONFLICT: {"description": "Email already registered"}},
)
async def register(payload: UserRegister, request: Request, db: AsyncSession = Depends(get_db)) -> User:
    # 감사 로그에 쓸 값: 주소 지문과 클라이언트 주소(주소 원문·비밀번호는 로그에 쓰지 않는다).
    fingerprint = email_fingerprint(payload.email)
    client = client_host(request)
    # payload.email은 EmailStr이 이미 정규화한 값이라 저장 형태와 같은 문자열로 중복을 확인한다.
    existing = await db.scalar(select(User).where(User.email == payload.email))
    if existing is not None:
        logger.warning("registration rejected reason=email_taken email=%s client=%s", fingerprint, client)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    # bcrypt는 호출마다 CPU를 약 0.25초 쓴다(cost 12). 이벤트 루프에서 그대로 돌리면 그동안 다른 요청이 모두
    # 멈추므로 작업 스레드에서 실행한다. 모델용 스레드 풀(run_model)은 쓰지 않는다: 로그인이 임베딩 계산 뒤에
    # 줄 서면 안 되기 때문이다.
    hashed = await run_in_threadpool(hash_password, payload.password)
    user = User(email=payload.email, hashed_password=hashed)
    db.add(user)
    # 동시에 같은 주소로 가입하면 두 요청이 위 확인을 함께 통과할 수 있다. 그때는 email 유일 제약이 늦은 쪽의
    # 삽입을 막아 commit이 IntegrityError를 낸다(먼저 쪽이 아직 commit하지 않았으면 PostgreSQL이 늦은 쪽
    # 삽입을 그 commit까지 기다리게 한 뒤 유일 제약 위반으로 끝낸다). 예전에는 이 예외가 그대로 올라가
    # 500이었다. 이제는 rollback으로 세션을 다시 쓸 수 있게 되돌리고(flush가 실패한 세션은 rollback 전까지
    # 다음 질의를 받지 않는다), 그 주소가 정말 등록돼 있는지 다시 확인해 위와 같은 409로 답한다. 다시 확인해도
    # 없으면 다른 무결성 오류이므로 원래 예외를 그대로 올린다(엉뚱한 409로 숨기지 않으려고).
    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        if await db.scalar(select(User.id).where(User.email == payload.email)) is None:
            raise
        logger.warning("registration rejected reason=email_taken email=%s client=%s", fingerprint, client)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered") from exc
    await db.refresh(user)
    logger.info("user registered user=%s email=%s client=%s", user.id, fingerprint, client)
    return user


# 로그인. 폼의 username 칸에 이메일을 넣는다(OAuth2 password 흐름 규약). 성공하면 접근·갱신 토큰 쌍을
# 돌려준다.
@router.post("/login", response_model=TokenPair)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> TokenPair:
    # 감사 로그에 쓸 값. 지문은 입력한 username으로 만든다(주소 형식이 아니어도 된다).
    fingerprint = email_fingerprint(form_data.username)
    client = client_host(request)
    # 가입은 EmailStr이 정규화한 형태(도메인을 소문자로)로 주소를 저장하므로, 입력한 username을 입력한
    # 그대로와 그 정규화한 형태 두 가지로 찾는다.
    user = await find_user_by_email(db, form_data.username)
    # 사용자가 없을 때와 비밀번호가 틀렸을 때 같은 401 메시지를 돌려줘, 어떤 이메일이 가입돼 있는지 응답
    # 내용으로는 알 수 없게 한다. (없는 이메일이면 bcrypt를 건너뛰므로 응답 시간 차이는 남는다.) 서버 로그에는
    # 두 경우를 reason으로 갈라 적는다(unknown_email / wrong_password). 응답에는 드러나지 않는다.
    # 72바이트를 넘는 비밀번호는 verify_password가 bcrypt를 부르지 않고 False를 돌려줘 500 대신 401이 된다.
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password"
    )
    if user is None:
        logger.warning("login failed reason=unknown_email email=%s client=%s", fingerprint, client)
        raise credentials_error
    if not await run_in_threadpool(verify_password, form_data.password, user.hashed_password):
        logger.warning(
            "login failed reason=wrong_password user=%s email=%s client=%s", user.id, fingerprint, client
        )
        raise credentials_error

    logger.info("login succeeded user=%s email=%s client=%s", user.id, fingerprint, client)
    return TokenPair(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


# 갱신 토큰으로 새 접근 토큰을 받는다. TokenType.REFRESH를 요구하므로 접근 토큰으로는 갱신할 수 없다.
# 서명·만료가 맞아도 사용자가 없거나 비활성이면 401이다. 갱신 토큰 자체는 새로 발급하지 않는다.
# 거부는 감사 로그 WARNING 한 줄로 남긴다: 토큰 자체가 무효면 reason=invalid_token과 decode_token의 고정
# 문구(detail), 서명은 맞지만 사용자가 없거나 비활성이면 reason=unknown_user / inactive_user와 토큰의 사용자
# id. 보낸 토큰 값은 적지 않는다. 성공한 갱신은 적지 않는다(새 자격 증명을 얻는 사건은 로그인 성공 줄로 이미
# 남고, 갱신은 그 로그인의 연장이다).
@router.post("/refresh", response_model=AccessToken)
async def refresh(
    payload: RefreshRequest, request: Request, db: AsyncSession = Depends(get_db)
) -> AccessToken:
    client = client_host(request)
    try:
        user_id = decode_token(payload.refresh_token, TokenType.REFRESH)
    except InvalidTokenError as exc:
        logger.warning("refresh rejected reason=invalid_token detail=%r client=%s", str(exc), client)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        ) from exc

    user = await db.get(User, user_id)
    if user is None or not user.is_active:
        reason = "unknown_user" if user is None else "inactive_user"
        logger.warning("refresh rejected reason=%s user=%s client=%s", reason, user_id, client)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    return AccessToken(access_token=create_access_token(user.id))


# 현재 로그인한 사용자 정보. 토큰이 유효한지 확인하는 가장 간단한 엔드포인트다.
@router.get("/me", response_model=UserOut)
async def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user

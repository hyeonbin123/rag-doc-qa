# [파일 역할] 라우터들이 Depends(...)로 받는 공용 의존성을 모은다. 로그인 사용자 확인, 언어별 임베딩·재정렬
# 모델 조회 함수, 생성기, 관리자 토큰 검사가 여기 있다.
# [왜 의존성으로 두나] 핸들러가 모델·서비스를 직접 만들지 않고 주입받으므로, 테스트는
# app.dependency_overrides로 가짜 임베딩·생성기·토큰 검사를 끼워 넣어 실제 모델이나 외부 API 없이 돌 수
# 있다(tests/conftest.py, tests/test_query.py, tests/test_documents.py).

from collections.abc import Callable

# FastAPI 의존성 도구와 OAuth2 Bearer 토큰 추출기, 그리고 앱 내부의 설정·DB 세션·서비스 조회 함수들을
# 가져온다.
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.db.session import get_db
from app.models.user import User
from app.services.embedding import EmbeddingService, get_embedding_service
from app.services.generation import GenerationService, get_generation_service
from app.services.language import Language
from app.services.reranking import RerankerService, get_reranker_service
from app.services.security import InvalidTokenError, TokenType, decode_token

# Authorization: Bearer <토큰> 헤더에서 토큰 문자열을 꺼내는 의존성. 헤더가 없으면 FastAPI가 401을 돌려준다.
# tokenUrl은 Swagger UI의 Authorize 버튼이 로그인할 주소다(/auth/login이 폼 형식으로 받는 이유).
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# 접근 토큰을 검증하고 그 토큰의 사용자 행을 돌려준다. /query/ask, /logs, /auth/me가 이것으로 로그인 사용자를
# 받는다.
# - decode_token에 TokenType.ACCESS를 넘겨, 수명이 긴 갱신 토큰을 접근 토큰 자리에 쓰지 못하게 한다.
# - 서명·만료가 맞아도 사용자가 지워졌거나 비활성(is_active=False)이면 거부한다.
# - 실패 이유와 상관없이 같은 401과 WWW-Authenticate: Bearer 헤더(OAuth2 Bearer 규약)를 돌려줘, 어떤 이유로
#   실패했는지 바깥에 알리지 않는다.
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        user_id = decode_token(token, TokenType.ACCESS)
    except InvalidTokenError as exc:
        raise credentials_error from exc

    user = await db.get(User, user_id)
    if user is None or not user.is_active:
        raise credentials_error
    return user


# 임베딩 모델 '하나'가 아니라 '언어 → 모델' 함수를 주입한다. 질문 언어는 요청 본문을 읽어야 알 수 있으므로,
# 핸들러가 언어를 정한 뒤 이 함수로 모델을 고른다. 적재 API도 문서 언어마다 이 함수를
# 쓴다(app/routers/documents.py).
def get_embedder() -> Callable[[Language], EmbeddingService]:
    # Returns the per-language lookup rather than one model: the question's language
    # decides which model embeds it.
    return get_embedding_service


# 설정(GENERATION_PROVIDER)에 맞는 답변 생성기를 돌려준다. 테스트는 이 의존성을 가짜 생성기로 바꾼다.
def get_generator() -> GenerationService:
    return get_generation_service()


# rerank 모드일 때만 '언어 → cross-encoder' 함수를, 아니면 None을 돌려준다. None이면 /query/ask가 재정렬 없이
# 검색한다. 재정렬 모델은 CPU에서 후보마다 돌려야 하는 비싼 모델이라(README '재정렬의 비용 관리') 쓰지 않는
# 모드에서는 올리지도 않는다.
def get_reranker(
    settings: Settings = Depends(get_settings),
) -> Callable[[Language], RerankerService] | None:
    # Only load a cross-encoder when the configured mode actually uses it. Like the
    # embedder, this is a per-language lookup.
    if settings.retrieval_mode != "rerank":
        return None
    return get_reranker_service


# 관리자 적재 API(/admin/documents/ingest)를 지키는 의존성. X-Admin-Token 헤더가 설정의 admin_ingest_token과
# 같아야 통과한다. Header(...)라 헤더가 아예 없으면 FastAPI가 422를, 값이 다르면 403을 돌려준다.
# 적재는 GitHub 접속, DB 변경, 사라진 문서 삭제까지 하는 작업이라 일반 JWT 사용자와 분리된 별도 토큰으로
# 막는다.
# 주의: 일반 문자열 비교(!=)라 상수 시간 비교는 아니다.
async def require_admin_token(
    x_admin_token: str = Header(...),
    settings: Settings = Depends(get_settings),
) -> None:
    if x_admin_token != settings.admin_ingest_token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid admin token")

# [파일 역할] FastAPI 애플리케이션 객체를 만들고 조립하는 진입점. uvicorn app.main:app으로
# 실행된다(Dockerfile, docker-compose.yml, README).
# [주요 구성]
# - lifespan: 서버 시작 때 언어별 임베딩 모델(rerank 모드면 재정렬 모델도)을 미리 올린다.
# - 422 처리기: 검증 오류 응답을 ASCII JSON으로 써서 고립 서로게이트 입력이 500이 되던 문제를 막고,
#   제출값(input)은 되돌려 주지 않는다.
# - 503 처리기: 생성기 장애(GenerationUnavailableError)를 503 + detail.code + Retry-After로 알린다.
# - 보안 헤더: 모든 응답에 CSP·클릭재킹 방지·nosniff 헤더를 붙인다(미들웨어, 그리고 미들웨어를 지나지 않는
#   예기치 않은 500은 500 처리기가 직접).
# - 라우터 5개(health, auth, documents, query, logs)와 채팅 화면(/, /static).
# [배경] 422 처리기와 보안 헤더는 OWASP ZAP 1차 스캔 지적(NUL 문자 500, CSP·클릭재킹·nosniff 헤더 없음)을
# 고치면서 들어왔다(docs/security-scan.md).

import json
import logging
from contextlib import asynccontextmanager
from pathlib import Path

# jsonable_encoder: 검증 오류 목록을 JSON으로 바꿀 수 있는 값으로 변환한다. RequestValidationError: 요청 검증
# 실패(422) 예외. JSONResponse·PlainTextResponse: 503·500 응답. FileResponse·StaticFiles: 채팅 화면 HTML과
# 정적 파일을 서빙한다.
from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse, Response
from fastapi.staticfiles import StaticFiles

# 앱 내부: 설정, 로깅 설정, 각 라우터, 시작 시 미리 올릴 모델 조회 함수, 생성기 장애 예외, 지원 언어 목록.
from app.config import get_settings, warn_if_weak_jwt_secret
from app.core.logging import configure_logging
from app.routers import auth, documents, health, logs, query
from app.services.embedding import get_embedding_service
from app.services.generation import GenerationUnavailableError
from app.services.language import SUPPORTED_LANGUAGES
from app.services.reranking import get_reranker_service

# 이 모듈의 로그(생성기 장애 한 줄). configure_logging의 형식으로 'app.main' 이름이 찍힌다.
logger = logging.getLogger(__name__)


# 서버 수명 주기 훅. yield 앞은 시작할 때, 뒤는 종료할 때 실행된다.
# 언어별 임베딩 모델을 시작할 때 한 번 올려 두면, 첫 질문이 모델 파일 로딩 시간까지 떠안지 않는다.
# get_*_service는 lru_cache라 여기서 만든 객체를 이후 요청이 그대로 쓴다. (Ollama 생성 모델은 별도 서버에
# 있으므로 여기서 올리지 않는다.)
# 재정렬 모델은 RETRIEVAL_MODE=rerank일 때만 올린다(기본 dense에서는 쓰지 않으므로).
# JWT 비밀키가 공개 예시 값이거나 짧으면 로깅을 켠 직후 큰 경고를 남긴다(APP_ENV=production이면 설정을 만들 때
# 이미 시작이 거부된다, app/config.py).
@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    settings = get_settings()
    warn_if_weak_jwt_secret(settings)
    rerank = settings.retrieval_mode == "rerank"
    for language in SUPPORTED_LANGUAGES:  # 시작할 때 언어마다 모델을 한 번씩 올린다
        get_embedding_service(language)
        if rerank:
            get_reranker_service(language)
    yield


# 앱 객체. title은 /docs(Swagger UI)와 OpenAPI 문서에 표시된다.
app = FastAPI(title="RAG Doc QA API", lifespan=lifespan)


# 422 본문에서 빼는 pydantic 오류 항목의 키. input은 제출한 값 그대로라 규칙에 걸린 비밀번호 원문, 필드가
# 빠졌을 때의 요청 본문 전체(/auth/refresh에서 키 이름을 틀리면 갱신 토큰도)가 들어 있었다. url은 pydantic
# 오류 문서 주소다. 화면(app/web/static/chat.js)과 테스트는 loc·type만 읽으므로, type·loc·msg·ctx(예:
# min_length)는 그대로 둔다.
VALIDATION_ERROR_DROPPED_KEYS = frozenset({"input", "url"})


# FastAPI 기본 422 처리기를 덮어쓴다. 응답 모양(detail 목록)은 기본과 같되 두 가지가 다르다.
# 1) 항목마다 input·url을 뺀다(위 VALIDATION_ERROR_DROPPED_KEYS). 기본 처리기는 제출값을 되돌려 줘, 거부된
#    비밀번호가 응답 본문에 실렸다.
# 2) 본문을 json.dumps(기본 ensure_ascii=True)로 만들어 한글 등 비ASCII 문자를 유니코드 이스케이프(백슬래시 u
#    네 자리)로 쓴다. 그러면 UTF-8로 인코딩할 수 없는 고립 서로게이트가 오류 문구 어디에 섞여도 응답 본문을
#    만들 수 있다.
@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc: RequestValidationError) -> Response:
    """FastAPI의 422 응답을 제출값 없이, ASCII만 쓰는 JSON으로 만든다.

    pydantic 오류 항목의 input(제출값)과 url은 빼고 type·loc·msg·ctx만 돌려준다. 예전에는 input이 그대로
    나가, 규칙에 걸린 비밀번호 원문이나 요청 본문 전체가 응답에 실렸다. 본문은 ASCII JSON으로 쓴다. JSON
    문자열에는 UTF-8로 나타낼 수 없는 고립 UTF-16 서로게이트("\\ud800")도 적을 수 있어, 본문을 UTF-8로
    인코딩하던 기본 처리에서는 이런 입력이 422 대신 500이 되었기 때문이다.
    """
    errors = [
        {key: value for key, value in error.items() if key not in VALIDATION_ERROR_DROPPED_KEYS}
        for error in exc.errors()
    ]
    body = json.dumps({"detail": jsonable_encoder(errors)})
    return Response(body, status_code=422, media_type="application/json")


# 생성기 장애(app/services/generation.py의 GenerationUnavailableError: Ollama·Claude 연결 실패, 시간 초과,
# 모델 없음)를 503으로 응답한다. 예전에는 예외가 그대로 올라가 트레이스백과 보안 헤더 없는 500이 됐고,
# 화면은 원인을 추측한 문구만 보였다.
# - 본문: {"detail": {"code": ..., "message": ...}}. code는 generator_unavailable / generator_timeout /
#   generator_model_missing, message는 영어 고정 문구. 채팅 화면은 code로 안내를 고른다.
# - Retry-After: 다시 시도할 만한 시간(초).
# - 업스트림 오류 본문(exc.upstream)은 응답에 싣지 않고 서버 로그 한 줄(WARNING)에만 남긴다. 운영자는 이
#   로그로 '우리 버그(500)'와 '생성기 장애(503)'를 가를 수 있다.
# - 생성은 질문 기록 저장 전 단계라 이 경우 query_logs에 행이 생기지 않는다(tests/test_query.py).
# 이 응답은 ExceptionMiddleware(사용자 미들웨어 안쪽)에서 만들어져 아래 security_headers를 지나므로 보안
# 헤더가 붙는다.
@app.exception_handler(GenerationUnavailableError)
async def generation_unavailable(request: Request, exc: GenerationUnavailableError) -> Response:
    logger.warning(
        "answer generator unavailable (%s) on %s %s: %s",
        exc.code,
        request.method,
        request.url.path,
        exc.upstream or "-",
    )
    return JSONResponse(
        {"detail": {"code": exc.code, "message": exc.message}},
        status_code=503,
        headers={"Retry-After": str(exc.retry_after)},
    )


# APP_CSP: 채팅 화면과 API 응답에 붙는 Content-Security-Policy. 모든 응답은 MIME 추측과 프레임 삽입을
# 막고(아래 security_headers), 채팅 화면과 API는 같은 출처의 코드만 허용한다. 화면의 스크립트·스타일은 /static
# 아래 파일이다.
# - default-src 'self': 같은 출처의 스크립트·스타일·이미지만 허용한다. 채팅 화면의 인라인 script·style을
#   app/web/static/chat.js·chat.css 파일로 옮긴 덕분에 'unsafe-inline' 없이 동작한다.
# - object-src 'none', base-uri 'none': 플러그인 삽입과 <base> 태그로 상대 경로를 가로채는 것을 막는다.
# - form-action 'self': 폼 전송 대상을 같은 출처로 제한한다.
# - frame-ancestors 'none': 다른 사이트가 이 페이지를 iframe에 넣지 못하게 한다(클릭재킹 방지).
APP_CSP = (
    "default-src 'self'; object-src 'none'; base-uri 'none'; form-action 'self'; "
    "frame-ancestors 'none'"
)
# DOCS_CSP: FastAPI가 자동으로 만드는 /docs, /docs/oauth2-redirect, /redoc에만 쓰는 느슨한 정책. 이 페이지들은
# jsDelivr CDN의 스크립트·스타일과 Google Fonts, 인라인 시작 코드를 쓰므로 APP_CSP로는 화면이 깨진다. 그래도
# frame-ancestors 'none'은 유지한다.
# DOCS_PATHS: FastAPI 객체가 실제로 쓰는 문서 경로를 그대로 읽어 와, 경로 설정이 바뀌어도 목록이 어긋나지 않게
# 한다.
# FastAPI 자체 문서 페이지는 Swagger UI와 ReDoc(그리고 ReDoc의 글꼴)을 CDN에서 불러와 인라인 코드로 시작한다.
# 인라인 코드를 해시로 하나씩 허용하는 방법도 있지만, jsDelivr를 허용한 시점에 이미 그곳의 어떤 패키지든
# 실행될 수 있으므로 정책이 크게 엄격해지지 않는다. 또 이 페이지들에는 사용자 데이터가 없어 'unsafe-inline'을
# 둔다.
DOCS_CSP = (
    "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
    "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; "
    "font-src 'self' https://fonts.gstatic.com; "
    "img-src 'self' data: https://fastapi.tiangolo.com https://cdn.redoc.ly; "
    "worker-src 'self' blob:; object-src 'none'; base-uri 'none'; form-action 'self'; "
    "frame-ancestors 'none'"
)
DOCS_PATHS = {app.docs_url, app.swagger_ui_oauth2_redirect_url, app.redoc_url}


# 응답에 붙일 보안 헤더 세 개(아래 미들웨어와 500 처리기가 함께 쓴다).
# - X-Content-Type-Options: nosniff: 브라우저가 Content-Type을 무시하고 내용을 추측해 실행하지 않게 한다.
# - X-Frame-Options: DENY: frame-ancestors를 모르는 오래된 브라우저를 위한 같은 뜻의 헤더.
# - 문서 페이지 경로면 DOCS_CSP, 나머지는 APP_CSP.
def security_header_values(path: str) -> dict[str, str]:
    return {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "Content-Security-Policy": DOCS_CSP if path in DOCS_PATHS else APP_CSP,
    }


# 모든 HTTP 응답(API, 채팅 화면, 정적 파일, 422·404·503 같은 처리된 오류 응답 포함)에 보안 헤더를 붙이는
# 미들웨어. 예기치 않은 예외의 500만은 이 미들웨어를 지나지 않으므로 아래 unexpected_error가 따로 붙인다.
@app.middleware("http")
async def security_headers(request: Request, call_next) -> Response:
    response = await call_next(request)
    response.headers.update(security_header_values(request.url.path))
    return response


# 예기치 않은 예외(처리기가 없는 모든 예외)의 500 응답. 본문은 Starlette 기본과 같은 text/plain
# 'Internal Server Error'이고, 보안 헤더 세 개만 더한다.
# - 왜 처리기가 필요한가: Starlette·FastAPI는 이 500을 사용자 미들웨어 바깥의 ServerErrorMiddleware에서 만든다
#   (Exception·500 처리기는 그 미들웨어의 handler가 된다). 그래서 security_headers 미들웨어는 이 응답을 보지
#   못하고, 미들웨어를 순수 ASGI로 바꿔도 마찬가지다. 여기서 같은 함수로 헤더를 붙인다.
# - 예외 내용은 응답에 싣지 않는다. ServerErrorMiddleware가 이 응답을 보낸 뒤 예외를 다시 올리므로, 서버
#   로그의 트레이스백은 예전처럼 남는다.
@app.exception_handler(Exception)
async def unexpected_error(request: Request, exc: Exception) -> Response:
    return PlainTextResponse(
        "Internal Server Error", status_code=500, headers=security_header_values(request.url.path)
    )


# 각 라우터의 경로를 앱에 등록한다: /health, /auth/*, /admin/documents/ingest·/documents, /query/ask, /logs.
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(query.router)
app.include_router(logs.router)

# 채팅 화면 파일 위치. 실행 위치(작업 폴더)와 상관없이 이 파일 기준 경로로 찾는다.
# /static에 app/web/static/(chat.js, chat.css)을 붙인다. CSP가 같은 출처 파일만 허용하므로 화면의
# 스크립트·스타일은 여기서 받아야 한다.
WEB_DIR = Path(__file__).parent / "web"
app.mount("/static", StaticFiles(directory=WEB_DIR / "static"), name="static")


# 브라우저로 루트 주소를 열면 채팅 화면(app/web/index.html)을 돌려준다. include_in_schema=False로 API
# 문서(OpenAPI, /docs)에는 나오지 않게 한다. 빌드가 필요한 별도 프론트엔드 대신 정적 HTML 한 장으로 둔 것은
# README '하지 않은 것'에 적힌 범위 결정이다.
@app.get("/", include_in_schema=False)
async def index() -> FileResponse:
    """브라우저에서 API를 써 보는 채팅 화면. 다른 클라이언트와 똑같은 엔드포인트를 호출한다."""
    return FileResponse(WEB_DIR / "index.html")

# [파일 역할] FastAPI 애플리케이션 객체를 만들고 조립하는 진입점. uvicorn app.main:app으로
# 실행된다(Dockerfile, docker-compose.yml, README).
# [주요 구성]
# - lifespan: 서버 시작 때 언어별 임베딩 모델(rerank 모드면 재정렬 모델도)을 미리 올린다.
# - 422 처리기: 검증 오류 응답을 ASCII JSON으로 써서 고립 서로게이트 입력이 500이 되던 문제를 막는다.
# - 보안 헤더 미들웨어: 모든 응답에 CSP·클릭재킹 방지·nosniff 헤더를 붙인다.
# - 라우터 5개(health, auth, documents, query, logs)와 채팅 화면(/, /static).
# [배경] 422 처리기와 보안 헤더는 OWASP ZAP 1차 스캔 지적(NUL 문자 500, CSP·클릭재킹·nosniff 헤더 없음)을
# 고치면서 들어왔다(docs/security-scan.md).

import json
from contextlib import asynccontextmanager
from pathlib import Path

# jsonable_encoder: 검증 오류 목록을 JSON으로 바꿀 수 있는 값으로 변환한다. RequestValidationError: 요청 검증
# 실패(422) 예외. FileResponse·StaticFiles: 채팅 화면 HTML과 정적 파일을 서빙한다.
from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles

# 앱 내부: 설정, 로깅 설정, 각 라우터, 시작 시 미리 올릴 모델 조회 함수, 지원 언어 목록.
from app.config import get_settings
from app.core.logging import configure_logging
from app.routers import auth, documents, health, logs, query
from app.services.embedding import get_embedding_service
from app.services.language import SUPPORTED_LANGUAGES
from app.services.reranking import get_reranker_service


# 서버 수명 주기 훅. yield 앞은 시작할 때, 뒤는 종료할 때 실행된다.
# 언어별 임베딩 모델을 시작할 때 한 번 올려 두면, 첫 질문이 모델 파일 로딩 시간까지 떠안지 않는다.
# get_*_service는 lru_cache라 여기서 만든 객체를 이후 요청이 그대로 쓴다. (Ollama 생성 모델은 별도 서버에
# 있으므로 여기서 올리지 않는다.)
# 재정렬 모델은 RETRIEVAL_MODE=rerank일 때만 올린다(기본 dense에서는 쓰지 않으므로).
@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    rerank = get_settings().retrieval_mode == "rerank"
    for language in SUPPORTED_LANGUAGES:  # 시작할 때 언어마다 모델을 한 번씩 올린다
        get_embedding_service(language)
        if rerank:
            get_reranker_service(language)
    yield


# 앱 객체. title은 /docs(Swagger UI)와 OpenAPI 문서에 표시된다.
app = FastAPI(title="RAG Doc QA API", lifespan=lifespan)


# FastAPI 기본 422 처리기를 덮어쓴다. 응답 모양(detail 목록)은 기본과 같고, 본문을 json.dumps(기본
# ensure_ascii=True)로 만들어 한글 등 비ASCII 문자를 유니코드 이스케이프(백슬래시 u 네 자리)로 쓴다는 점만
# 다르다. 그러면 UTF-8로 인코딩할 수 없는 고립 서로게이트가 입력에 섞여 와도 응답 본문을 만들 수 있다.
@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc: RequestValidationError) -> Response:
    """FastAPI의 422 응답을 ASCII만 쓰는 JSON으로 만든다.

    오류 목록은 입력값을 그대로 되돌려 주는데, JSON 문자열에는 UTF-8로 나타낼 수 없는 고립 UTF-16
    서로게이트("\\ud800")도 적을 수 있다. 그래서 본문을 UTF-8로 인코딩하던 기본 처리에서는 이런 입력이
    422 대신 500이 되었다.
    """
    body = json.dumps({"detail": jsonable_encoder(exc.errors())})
    return Response(body, status_code=422, media_type="application/json")


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


# 모든 HTTP 응답(API, 채팅 화면, 정적 파일, 오류 응답 포함)에 보안 헤더를 붙이는 미들웨어.
# - X-Content-Type-Options: nosniff: 브라우저가 Content-Type을 무시하고 내용을 추측해 실행하지 않게 한다.
# - X-Frame-Options: DENY: frame-ancestors를 모르는 오래된 브라우저를 위한 같은 뜻의 헤더.
# - 문서 페이지 경로면 DOCS_CSP, 나머지는 APP_CSP.
@app.middleware("http")
async def security_headers(request: Request, call_next) -> Response:
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Content-Security-Policy"] = (
        DOCS_CSP if request.url.path in DOCS_PATHS else APP_CSP
    )
    return response


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

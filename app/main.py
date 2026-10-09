import json
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.core.logging import configure_logging
from app.routers import auth, documents, health, logs, query
from app.services.embedding import get_embedding_service
from app.services.language import SUPPORTED_LANGUAGES
from app.services.reranking import get_reranker_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    rerank = get_settings().retrieval_mode == "rerank"
    for language in SUPPORTED_LANGUAGES:  # load each language's models once at startup
        get_embedding_service(language)
        if rerank:
            get_reranker_service(language)
    yield


app = FastAPI(title="RAG Doc QA API", lifespan=lifespan)


@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc: RequestValidationError) -> Response:
    """FastAPI's 422, written as ASCII JSON.

    The errors echo the input, and JSON can spell a lone UTF-16 surrogate ("\\ud800") that
    has no UTF-8 form, so encoding the body as UTF-8 turned the 422 into a 500.
    """
    body = json.dumps({"detail": jsonable_encoder(exc.errors())})
    return Response(body, status_code=422, media_type="application/json")


# Every response: no MIME sniffing, no framing. The chat page and the API allow only
# same-origin code; the page's script and style are files under /static.
APP_CSP = (
    "default-src 'self'; object-src 'none'; base-uri 'none'; form-action 'self'; "
    "frame-ancestors 'none'"
)
# FastAPI's own docs pages load Swagger UI and ReDoc (and ReDoc's fonts) from CDNs and start
# them with inline code. Allowing jsDelivr already lets any package there run, so hashing the
# inline code would not make this policy much stricter; the pages hold no user data.
DOCS_CSP = (
    "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
    "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; "
    "font-src 'self' https://fonts.gstatic.com; "
    "img-src 'self' data: https://fastapi.tiangolo.com https://cdn.redoc.ly; "
    "worker-src 'self' blob:; object-src 'none'; base-uri 'none'; form-action 'self'; "
    "frame-ancestors 'none'"
)
DOCS_PATHS = {app.docs_url, app.swagger_ui_oauth2_redirect_url, app.redoc_url}


@app.middleware("http")
async def security_headers(request: Request, call_next) -> Response:
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Content-Security-Policy"] = (
        DOCS_CSP if request.url.path in DOCS_PATHS else APP_CSP
    )
    return response


app.include_router(health.router)
app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(query.router)
app.include_router(logs.router)

WEB_DIR = Path(__file__).parent / "web"
app.mount("/static", StaticFiles(directory=WEB_DIR / "static"), name="static")


@app.get("/", include_in_schema=False)
async def index() -> FileResponse:
    """Chat page for trying the API in a browser; it calls the same endpoints as any client."""
    return FileResponse(WEB_DIR / "index.html")

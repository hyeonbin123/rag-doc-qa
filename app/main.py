import json
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, Response

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


app.include_router(health.router)
app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(query.router)
app.include_router(logs.router)

WEB_DIR = Path(__file__).parent / "web"


@app.get("/", include_in_schema=False)
async def index() -> FileResponse:
    """Chat page for trying the API in a browser; it calls the same endpoints as any client."""
    return FileResponse(WEB_DIR / "index.html")

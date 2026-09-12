from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

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

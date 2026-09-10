from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.logging import configure_logging
from app.routers import auth, documents, health, logs, query
from app.services.embedding import get_embedding_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    get_embedding_service()  # load the embedding model once at startup
    yield


app = FastAPI(title="RAG Doc QA API", lifespan=lifespan)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(query.router)
app.include_router(logs.router)

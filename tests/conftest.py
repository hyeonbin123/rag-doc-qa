"""Test fixtures.

Integration tests (test_auth.py, test_retrieval.py, test_query.py) need a
running Postgres+pgvector instance reachable via TEST_DATABASE_URL (defaults
to the docker-compose db on a separate "ragdb_test" database). Run
`docker compose up -d db` before `pytest`.
"""

import os

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.db.base import Base
from app.db.session import get_db
from app.dependencies import get_embedder, get_generator
from app.main import app
from app.services.embedding import EmbeddingService
from app.services.generation import GenerationResult, GenerationService

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://raguser:ragpass@localhost:5432/ragdb_test",
)

EMBEDDING_DIM = 384


class FakeEmbeddingService(EmbeddingService):
    """Deterministic, dependency-free stand-in for the real sentence-transformer model."""

    def __init__(self) -> None:  # intentionally skip the real __init__/model load
        pass

    def _fake_vector(self, text: str) -> list[float]:
        seed = sum(text.encode("utf-8")) or 1
        return [((seed * (i + 1)) % 997) / 997 for i in range(EMBEDDING_DIM)]

    def embed_query(self, text: str) -> list[float]:
        return self._fake_vector(text)

    def embed_passages(self, texts: list[str]) -> list[list[float]]:
        return [self._fake_vector(t) for t in texts]


class FakeGenerationService(GenerationService):
    async def answer(self, question, chunks):
        cited = list(range(1, len(chunks) + 1))
        return GenerationResult(
            answer=f"Fake answer for: {question}",
            cited_chunk_numbers=cited,
            input_tokens=10,
            output_tokens=10,
            model_name="fake-model",
        )


@pytest_asyncio.fixture
async def db_engine():
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine):
    session_maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with session_maker() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_embedder] = lambda: FakeEmbeddingService()
    app.dependency_overrides[get_generator] = lambda: FakeGenerationService()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def authed_client(client, db_session):
    resp = await client.post(
        "/auth/register", json={"email": "test@example.com", "password": "testpass123"}
    )
    assert resp.status_code == 201

    login_resp = await client.post(
        "/auth/login",
        data={"username": "test@example.com", "password": "testpass123"},
    )
    token = login_resp.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    yield client

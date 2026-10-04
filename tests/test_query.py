import pytest

from app.dependencies import get_embedder, get_generator
from app.main import app
from app.models.chunk import Chunk
from app.models.document import Document
from app.services import retrieval
from tests.conftest import EMBEDDING_DIM, FakeEmbeddingService, FakeGenerationService


class TransactionProbeGenerator(FakeGenerationService):
    """Records whether the request's DB session still holds a connection while generating."""

    def __init__(self, session) -> None:
        self.session = session
        self.in_transaction: bool | None = None
        self.connections_checked_out: int | None = None

    async def answer(self, question, chunks, language="en"):
        self.in_transaction = self.session.in_transaction()
        self.connections_checked_out = self.session.bind.pool.checkedout()
        return await super().answer(question, chunks, language)


@pytest.mark.asyncio
async def test_ask_requires_auth(client):
    resp = await client.post("/query/ask", json={"question": "How do path params work?"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_ask_returns_answer_with_citations(authed_client, db_session):
    fake_embedder = FakeEmbeddingService()
    vector = fake_embedder.embed_query("How do path params work?")

    document = Document(
        source_path="docs/en/docs/tutorial/path-params.md",
        title="Path Parameters",
        source_commit_sha="deadbeef",
        content_hash="hash-path-params",
    )
    db_session.add(document)
    await db_session.flush()

    chunk = Chunk(
        document_id=document.id,
        chunk_index=0,
        heading_path="Tutorial > Path Parameters",
        content="You can declare path parameters using type hints.",
        token_count=10,
        embedding=vector,
    )
    db_session.add(chunk)
    await db_session.commit()

    resp = await authed_client.post(
        "/query/ask", json={"question": "How do path params work?", "top_k": 3}
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["answer"].startswith("Fake answer for:")
    assert len(body["citations"]) >= 1
    assert body["citations"][0]["source_path"] == "docs/en/docs/tutorial/path-params.md"
    assert body["latency_ms"]["total"] >= 0


@pytest.mark.asyncio
async def test_ask_persists_query_log(authed_client, db_session):
    resp = await authed_client.post("/query/ask", json={"question": "What is FastAPI?"})
    assert resp.status_code == 200
    log_id = resp.json()["query_log_id"]

    log_resp = await authed_client.get(f"/logs/{log_id}")
    assert log_resp.status_code == 200
    assert log_resp.json()["question"] == "What is FastAPI?"


@pytest.mark.asyncio
async def test_ask_releases_db_connection_during_generation(authed_client, db_session):
    # Generation takes seconds and Ollama answers one request at a time, so a question
    # that kept its pooled connection through it would starve every other endpoint.
    probe = TransactionProbeGenerator(db_session)
    app.dependency_overrides[get_generator] = lambda: probe

    resp = await authed_client.post("/query/ask", json={"question": "What is FastAPI?"})

    assert resp.status_code == 200
    assert probe.in_transaction is False
    assert probe.connections_checked_out == 0
    # The query log is still written afterwards, in its own short transaction.
    log_resp = await authed_client.get(f"/logs/{resp.json()['query_log_id']}")
    assert log_resp.status_code == 200


class AxisEmbeddingService(FakeEmbeddingService):
    """Embeds every question as the first axis, so a chunk's score is its first component."""

    def __init__(self) -> None:
        self.model_name = "axis-embedding"

    def embed_query(self, text: str) -> list[float]:
        return [1.0] + [0.0] * (EMBEDDING_DIM - 1)


@pytest.mark.asyncio
async def test_ask_uses_the_score_floor_of_the_embedding_model(authed_client, db_session, monkeypatch):
    document = Document(
        source_path="docs/en/docs/tutorial/body.md",
        title="Body",
        source_commit_sha="deadbeef",
        content_hash="hash-body",
    )
    db_session.add(document)
    await db_session.flush()
    db_session.add(
        Chunk(
            document_id=document.id,
            chunk_index=0,
            heading_path="Body",
            content="Declare a Pydantic model.",
            token_count=5,
            embedding=[0.25, (1 - 0.25**2) ** 0.5] + [0.0] * (EMBEDDING_DIM - 2),  # cosine 0.25
        )
    )
    await db_session.commit()
    app.dependency_overrides[get_embedder] = lambda: lambda language="en": AxisEmbeddingService()

    under_shared_floor = await authed_client.post("/query/ask", json={"question": "Body?"})
    monkeypatch.setitem(retrieval.SCORE_FLOORS, "axis-embedding", 0.2)
    under_model_floor = await authed_client.post("/query/ask", json={"question": "Body?"})

    assert under_shared_floor.json()["citations"] == []
    assert [c["source_path"] for c in under_model_floor.json()["citations"]] == [
        "docs/en/docs/tutorial/body.md"
    ]

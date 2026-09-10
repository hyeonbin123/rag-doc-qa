import pytest

from app.models.chunk import Chunk
from app.models.document import Document
from tests.conftest import FakeEmbeddingService


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

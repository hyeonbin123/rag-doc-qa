import pytest

from app.models.chunk import Chunk
from app.models.document import Document
from app.services.retrieval import similarity_search
from tests.conftest import EMBEDDING_DIM


async def _seed_document_with_chunk(db_session, embedding: list[float], content: str):
    document = Document(
        source_path=f"docs/en/docs/{content[:10]}.md",
        title="Test Doc",
        source_commit_sha="deadbeef",
        content_hash="hash-" + content[:10],
    )
    db_session.add(document)
    await db_session.flush()

    chunk = Chunk(
        document_id=document.id,
        chunk_index=0,
        heading_path="Tutorial > Test",
        content=content,
        token_count=10,
        embedding=embedding,
    )
    db_session.add(chunk)
    await db_session.commit()
    return document, chunk


@pytest.mark.asyncio
async def test_similarity_search_returns_closest_chunk(db_session):
    exact_vector = [1.0] + [0.0] * (EMBEDDING_DIM - 1)
    far_vector = [0.0] * (EMBEDDING_DIM - 1) + [1.0]

    await _seed_document_with_chunk(db_session, exact_vector, "relevant content")
    await _seed_document_with_chunk(db_session, far_vector, "irrelevant content")

    results = await similarity_search(db_session, exact_vector, top_k=5)

    assert len(results) >= 1
    assert results[0].content == "relevant content"


@pytest.mark.asyncio
async def test_similarity_search_respects_top_k(db_session):
    for i in range(5):
        vector = [float(i)] + [0.0] * (EMBEDDING_DIM - 1)
        await _seed_document_with_chunk(db_session, vector, f"content {i}")

    query_vector = [0.0] * EMBEDDING_DIM
    results = await similarity_search(db_session, query_vector, top_k=2)

    assert len(results) <= 2

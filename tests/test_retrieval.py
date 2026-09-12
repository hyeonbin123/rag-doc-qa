import pytest

from app.models.chunk import Chunk
from app.models.document import Document
from app.services.reranking import RerankerService
from app.services.retrieval import (
    RERANK_POOLS,
    hybrid_search,
    lexical_search,
    rerank_search,
    retrieve,
    similarity_search,
)
from tests.conftest import EMBEDDING_DIM


class KeywordReranker(RerankerService):
    """Stands in for the cross-encoder: 1.0 if the passage has the keyword, else 0.0."""

    def __init__(self, keyword: str) -> None:  # intentionally skip loading a real model
        self.keyword = keyword
        self.last_candidate_count = 0

    def score(self, question: str, passages: list[str]) -> list[float]:
        self.last_candidate_count = len(passages)
        return [1.0 if self.keyword in p else 0.0 for p in passages]


async def _seed_document_with_chunk(
    db_session, embedding: list[float], content: str, language: str = "en"
):
    document = Document(
        source_path=f"docs/{language}/docs/{content[:10]}.md",
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
        language=language,
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


@pytest.mark.asyncio
async def test_hybrid_search_surfaces_lexical_match_that_dense_drops(db_session):
    query_vector = [1.0] + [0.0] * (EMBEDDING_DIM - 1)
    orthogonal = [0.0] * (EMBEDDING_DIM - 1) + [1.0]
    await _seed_document_with_chunk(db_session, query_vector, "generic prose about nothing much")
    await _seed_document_with_chunk(db_session, orthogonal, "load settings from environment variables")

    dense = await similarity_search(db_session, query_vector, top_k=5)
    assert all("environment" not in r.content for r in dense)  # cosine 0 falls under the floor

    hybrid = await hybrid_search(db_session, "environment variables", query_vector, top_k=5)
    assert "environment" in hybrid[0].content


@pytest.mark.asyncio
async def test_lexical_search_ranks_rare_terms_above_repeated_common_ones(db_session):
    vector = [1.0] + [0.0] * (EMBEDDING_DIM - 1)
    await _seed_document_with_chunk(db_session, vector, "fastapi fastapi fastapi tutorial")
    await _seed_document_with_chunk(db_session, vector, "fastapi credentials")
    await _seed_document_with_chunk(db_session, vector, "fastapi basics")

    # Without IDF the chunk repeating "fastapi" would win; BM25 weights the word that
    # only one chunk contains far above the word every chunk contains.
    results = await lexical_search(db_session, "fastapi credentials", top_k=5)
    assert results[0].content == "fastapi credentials"


@pytest.mark.asyncio
async def test_hybrid_search_with_only_stopwords_still_returns_dense_results(db_session):
    vector = [1.0] + [0.0] * (EMBEDDING_DIM - 1)
    await _seed_document_with_chunk(db_session, vector, "some content")

    results = await hybrid_search(db_session, "how is it", vector, top_k=5)
    assert [r.content for r in results] == ["some content"]


@pytest.mark.asyncio
async def test_hybrid_search_without_searchable_words_falls_back_to_dense(db_session):
    vector = [1.0] + [0.0] * (EMBEDDING_DIM - 1)
    await _seed_document_with_chunk(db_session, vector, "some content")

    results = await hybrid_search(db_session, "?!", vector, top_k=5)
    assert [r.content for r in results] == ["some content"]


@pytest.mark.asyncio
async def test_rerank_search_reorders_the_union_of_dense_and_bm25_candidates(db_session):
    query_vector = [1.0] + [0.0] * (EMBEDDING_DIM - 1)
    orthogonal = [0.0] * (EMBEDDING_DIM - 1) + [1.0]
    await _seed_document_with_chunk(db_session, query_vector, "generic prose about nothing much")
    await _seed_document_with_chunk(db_session, orthogonal, "load settings from environment variables")

    # One candidate per list: dense brings the generic chunk, BM25 the environment one,
    # and the order comes from the reranker alone.
    results = await rerank_search(
        db_session,
        "environment variables",
        query_vector,
        top_k=2,
        reranker=KeywordReranker("environment"),
        pool=1,
    )
    assert [r.content for r in results] == [
        "load settings from environment variables",
        "generic prose about nothing much",
    ]
    assert results[0].score == 1.0


@pytest.mark.asyncio
async def test_rerank_search_respects_top_k(db_session):
    for i in range(3):
        vector = [1.0, float(i)] + [0.0] * (EMBEDDING_DIM - 2)
        await _seed_document_with_chunk(db_session, vector, f"{i} content")

    query_vector = [1.0] + [0.0] * (EMBEDDING_DIM - 1)
    results = await rerank_search(
        db_session, "content", query_vector, top_k=2, reranker=KeywordReranker("content")
    )
    assert len(results) == 2


@pytest.mark.asyncio
async def test_rerank_pool_defaults_to_the_questions_language(db_session):
    for i in range(8):
        vector = [1.0, 0.1 * i] + [0.0] * (EMBEDDING_DIM - 2)
        await _seed_document_with_chunk(db_session, vector, f"{i} english chunk", "en")
        await _seed_document_with_chunk(db_session, vector, f"{i} 한국어 청크", "ko")

    # Neither question has [A-Za-z0-9] words, so the dense list is the only source of
    # candidates and its length is exactly the pool.
    query_vector = [1.0] + [0.0] * (EMBEDDING_DIM - 1)
    reranker = KeywordReranker("chunk")
    await rerank_search(db_session, "?!", query_vector, 10, reranker, language="en")
    assert reranker.last_candidate_count == RERANK_POOLS["en"]
    await rerank_search(db_session, "청크를 찾아 주세요", query_vector, 10, reranker, language="ko")
    assert reranker.last_candidate_count == RERANK_POOLS["ko"]


@pytest.mark.asyncio
async def test_retrieve_only_searches_the_question_language(db_session):
    vector = [1.0] + [0.0] * (EMBEDDING_DIM - 1)
    await _seed_document_with_chunk(db_session, vector, "english chunk about errors", "en")
    await _seed_document_with_chunk(db_session, vector, "한국어 오류 처리 청크", "ko")

    ko = await retrieve(db_session, "오류는 어떻게 처리하나요?", vector, 5, "dense")
    en = await retrieve(db_session, "How are errors handled?", vector, 5, "dense")
    forced = await retrieve(db_session, "HTTPException", vector, 5, "hybrid", language="ko")

    assert [r.content for r in ko] == ["한국어 오류 처리 청크"]
    assert [r.content for r in en] == ["english chunk about errors"]
    assert [r.content for r in forced] == ["한국어 오류 처리 청크"]


@pytest.mark.asyncio
async def test_unsupported_language_is_rejected_before_reaching_sql(db_session):
    vector = [1.0] + [0.0] * (EMBEDDING_DIM - 1)
    with pytest.raises(ValueError):
        await similarity_search(db_session, vector, 5, "xx'; DROP TABLE chunks; --")


@pytest.mark.asyncio
async def test_retrieve_in_rerank_mode_requires_a_reranker(db_session):
    with pytest.raises(ValueError):
        await retrieve(db_session, "q", [1.0] + [0.0] * (EMBEDDING_DIM - 1), 5, "rerank")

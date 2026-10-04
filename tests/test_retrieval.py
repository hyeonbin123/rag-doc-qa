import pytest

from app.models.chunk import Chunk
from app.models.document import Document
from app.services.reranking import RerankerService
from app.services.retrieval import (
    RERANK_POOLS,
    SCORE_FLOOR,
    SCORE_FLOORS,
    cross_lingual_search,
    hybrid_search,
    lexical_search,
    page_key,
    rerank_search,
    retrieve,
    score_floor_for,
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


# --- score floor per embedding model, cross-lingual search (docs/experiments.md v12) ---


def _unit(*components: float) -> list[float]:
    """A vector whose first components are given and the rest zero."""
    return list(components) + [0.0] * (EMBEDDING_DIM - len(components))


def _at_similarity(cosine: float) -> list[float]:
    """A unit vector whose cosine with _unit(1.0) is `cosine`."""
    return _unit(cosine, (1 - cosine**2) ** 0.5)


async def _seed_page_chunk(db_session, path: str, embedding: list[float], content: str, index: int = 0):
    """A chunk of the page at `path`; the page's document is created on first use."""
    from sqlalchemy import select

    document = await db_session.scalar(select(Document).where(Document.source_path == path))
    if document is None:
        document = Document(
            source_path=path, title="T", source_commit_sha="deadbeef", content_hash="h-" + path
        )
        db_session.add(document)
        await db_session.flush()
    db_session.add(
        Chunk(
            document_id=document.id,
            chunk_index=index,
            heading_path="H",
            content=content,
            token_count=10,
            embedding=embedding,
            language=path.split("/")[1],
        )
    )
    await db_session.commit()


@pytest.mark.asyncio
async def test_similarity_search_takes_the_score_floor_as_a_parameter(db_session):
    await _seed_page_chunk(db_session, "docs/en/docs/low.md", _at_similarity(0.25), "low score")

    assert await similarity_search(db_session, _unit(1.0), 5) == []  # under the default 0.3
    lowered = await similarity_search(db_session, _unit(1.0), 5, score_floor=0.2)
    assert [r.content for r in lowered] == ["low score"]


def test_models_without_a_measured_floor_use_the_shared_one(monkeypatch):
    assert score_floor_for("intfloat/multilingual-e5-small") == SCORE_FLOOR
    monkeypatch.setitem(SCORE_FLOORS, "some/model", 0.15)
    assert score_floor_for("some/model") == 0.15


def test_page_key_is_the_same_for_every_translation_of_a_page():
    assert page_key("docs/ko/docs/tutorial/body.md") == "tutorial/body.md"
    assert page_key("docs/en/docs/tutorial/body.md") == "tutorial/body.md"
    assert page_key("docs/en/docs/index.md") == "index.md"
    assert page_key("README.md") == "README.md"  # not a docs page: left as it is


@pytest.mark.asyncio
async def test_cross_lingual_search_keeps_one_translation_per_page(db_session):
    await _seed_page_chunk(db_session, "docs/ko/docs/a.md", _at_similarity(0.9), "ko a")
    await _seed_page_chunk(db_session, "docs/en/docs/a.md", _at_similarity(0.8), "en a")
    await _seed_page_chunk(db_session, "docs/en/docs/b.md", _at_similarity(0.7), "en b")
    await _seed_page_chunk(db_session, "docs/ko/docs/b.md", _at_similarity(0.6), "ko b")

    results = await cross_lingual_search(db_session, _unit(1.0), 5, ("ko", "en"))

    # Page a is taken by its Korean chunk and page b by its English one, so the other
    # translation of each page is dropped instead of repeating the same content.
    assert [r.content for r in results] == ["ko a", "en b"]


@pytest.mark.asyncio
async def test_cross_lingual_search_keeps_several_chunks_of_a_page_in_one_language(db_session):
    await _seed_page_chunk(db_session, "docs/ko/docs/a.md", _at_similarity(0.9), "ko a 1", 0)
    await _seed_page_chunk(db_session, "docs/ko/docs/a.md", _at_similarity(0.8), "ko a 2", 1)
    await _seed_page_chunk(db_session, "docs/en/docs/c.md", _at_similarity(0.7), "en c")

    results = await cross_lingual_search(db_session, _unit(1.0), 2, ("ko", "en"))

    assert [r.content for r in results] == ["ko a 1", "ko a 2"]


@pytest.mark.asyncio
async def test_cross_lingual_search_applies_the_floor_to_both_languages(db_session):
    await _seed_page_chunk(db_session, "docs/ko/docs/a.md", _at_similarity(0.25), "ko a")
    await _seed_page_chunk(db_session, "docs/en/docs/b.md", _at_similarity(0.28), "en b")

    assert await cross_lingual_search(db_session, _unit(1.0), 5, ("ko", "en")) == []
    lowered = await cross_lingual_search(db_session, _unit(1.0), 5, ("ko", "en"), score_floor=0.2)
    assert [r.content for r in lowered] == ["en b", "ko a"]


@pytest.mark.asyncio
async def test_retrieve_searches_every_translation_only_when_asked(db_session):
    await _seed_page_chunk(db_session, "docs/ko/docs/a.md", _at_similarity(0.6), "ko a")
    await _seed_page_chunk(db_session, "docs/en/docs/b.md", _at_similarity(0.9), "en b")

    plain = await retrieve(db_session, "질문", _unit(1.0), 5, "dense", language="ko")
    crossed = await retrieve(
        db_session, "질문", _unit(1.0), 5, "dense", language="ko", cross_lingual=True
    )

    assert [r.content for r in plain] == ["ko a"]
    assert [r.content for r in crossed] == ["en b", "ko a"]


@pytest.mark.asyncio
async def test_retrieve_passes_the_score_floor_to_dense_search(db_session):
    await _seed_page_chunk(db_session, "docs/ko/docs/a.md", _at_similarity(0.25), "ko a")

    assert await retrieve(db_session, "질문", _unit(1.0), 5, "dense", language="ko") == []
    lowered = await retrieve(
        db_session, "질문", _unit(1.0), 5, "dense", language="ko", score_floor=0.2
    )
    assert [r.content for r in lowered] == ["ko a"]


@pytest.mark.asyncio
async def test_cross_lingual_retrieval_is_dense_only(db_session):
    with pytest.raises(ValueError):
        await retrieve(db_session, "질문", _unit(1.0), 5, "hybrid", language="ko", cross_lingual=True)

# [테스트 묶음] 검색 서비스(app/services/retrieval.py)의 통합 테스트. 실제 테스트 DB에 손으로 만든 벡터의
# 청크를 넣어 dense·BM25·hybrid·rerank·교차언어 검색과 점수 바닥값이 SQL까지 포함해 의도대로 순위를 내는지
# 확인한다.
# [왜 중요한가] 검색 모드의 동작은 docs/experiments.md v4~v12의 결정 근거다. 예를 들어 BM25가 IDF로 드문
# 단어를 높이 치는지(v5), 언어별 인덱스에서 그 언어만 찾는지(v8), 재정렬 후보 수가 언어를 따르는지(v9),
# 교차언어 검색이 페이지당 한 번역만 남기는지(v12)를 고정한다.
# [방법] 벡터를 축 방향 단위 벡터로 만들어 코사인 점수를 정확히 정하고, cross-encoder는 키워드가 있으면 1.0을
# 주는 가짜로 바꾼다.

import pytest

# 테스트 데이터로 넣을 문서·청크 모델, 가짜 재정렬기가 상속할 RerankerService, 테스트 대상 검색 함수와 설정값,
# 벡터 차원(384).
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


# cross-encoder 대신 쓰는 가짜 재정렬기: 패시지에 키워드가 있으면 1.0, 없으면 0.0. 받은 후보 수도 기록해 후보
# 수(pool) 테스트에 쓴다. 실제 모델은 올리지 않는다.
class KeywordReranker(RerankerService):
    """cross-encoder 대역: 문단에 키워드가 있으면 1.0, 없으면 0.0."""

    def __init__(self, keyword: str) -> None:  # 실제 모델 로딩을 일부러 건너뛴다
        self.keyword = keyword
        self.last_candidate_count = 0

    def score(self, question: str, passages: list[str]) -> list[float]:
        self.last_candidate_count = len(passages)
        return [1.0 if self.keyword in p else 0.0 for p in passages]


# 문서 하나와 그 청크 하나를 지정한 벡터·본문·언어로 넣고 커밋한다. 문서 경로와 해시는 본문 앞 10글자로 만들어
# 테스트마다 다르게 한다.
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


# 질문과 같은 벡터의 청크가 1위로 나오는지 확인한다. 직교하는 청크는 코사인 0이라 바닥값(0.3) 아래로 잘린다.
@pytest.mark.asyncio
async def test_similarity_search_returns_closest_chunk(db_session):
    exact_vector = [1.0] + [0.0] * (EMBEDDING_DIM - 1)
    far_vector = [0.0] * (EMBEDDING_DIM - 1) + [1.0]

    await _seed_document_with_chunk(db_session, exact_vector, "relevant content")
    await _seed_document_with_chunk(db_session, far_vector, "irrelevant content")

    results = await similarity_search(db_session, exact_vector, top_k=5)

    assert len(results) >= 1
    assert results[0].content == "relevant content"


# 결과가 top_k개로 잘리는지 확인한다. 다섯 청크 모두 바닥값(0.3)을 넘는 점수라, 결과 수를 줄이는 것은
# top_k뿐이다. 예전 테스트는 질문 벡터가 영벡터였는데, pgvector는 영벡터와의 코사인 거리를 NaN으로 내서 모든
# 결과가 바닥값 비교에서 빠졌다. 결과 0개로도 'len <= 2'가 통과해 top_k를 확인하지 못했다.
@pytest.mark.asyncio
async def test_similarity_search_respects_top_k(db_session):
    for i, cosine in enumerate((0.9, 0.8, 0.7, 0.6, 0.5)):
        await _seed_document_with_chunk(db_session, _at_similarity(cosine), f"content {i}")

    results = await similarity_search(db_session, _unit(1.0), top_k=2)

    assert [r.content for r in results] == ["content 0", "content 1"]


# dense에서는 코사인 0이라 바닥값에 잘리는 청크도, 질문 단어가 본문에 있으면 hybrid(벡터 + BM25를 가중 RRF로
# 합침)에서 1위로 올라오는지 확인한다. hybrid를 둔 이유(어휘가 맞는 문서를 dense가 놓치는 경우, v4)를
# 고정한다.
@pytest.mark.asyncio
async def test_hybrid_search_surfaces_lexical_match_that_dense_drops(db_session):
    query_vector = [1.0] + [0.0] * (EMBEDDING_DIM - 1)
    orthogonal = [0.0] * (EMBEDDING_DIM - 1) + [1.0]
    await _seed_document_with_chunk(db_session, query_vector, "generic prose about nothing much")
    await _seed_document_with_chunk(db_session, orthogonal, "load settings from environment variables")

    dense = await similarity_search(db_session, query_vector, top_k=5)
    assert all("environment" not in r.content for r in dense)  # 코사인 0은 바닥값 아래라 버려진다

    hybrid = await hybrid_search(db_session, "environment variables", query_vector, top_k=5)
    assert "environment" in hybrid[0].content


# BM25가 IDF를 반영하는지 확인한다: 모든 청크에 있는 'fastapi'를 세 번 반복한 청크보다, 한 청크에만 있는 드문
# 단어 'credentials'를 가진 청크가 1위여야 한다. Postgres ts_rank는 IDF가 없어 이 경우를 거꾸로 매겼고, 그것이
# v4 hybrid가 진 원인이었다(docs/experiments.md v4·v5).
@pytest.mark.asyncio
async def test_lexical_search_ranks_rare_terms_above_repeated_common_ones(db_session):
    vector = [1.0] + [0.0] * (EMBEDDING_DIM - 1)
    await _seed_document_with_chunk(db_session, vector, "fastapi fastapi fastapi tutorial")
    await _seed_document_with_chunk(db_session, vector, "fastapi credentials")
    await _seed_document_with_chunk(db_session, vector, "fastapi basics")

    # IDF가 없으면 "fastapi"를 반복한 청크가 이긴다. BM25는 한 청크에만 있는 단어를 모든 청크에 있는 단어보다
    # 훨씬 무겁게 친다.
    results = await lexical_search(db_session, "fastapi credentials", top_k=5)
    assert results[0].content == "fastapi credentials"


# 질문이 불용어뿐이면('how is it') BM25 쪽에 검색어가 남지 않아도 오류 없이 dense 결과만 돌려준다.
@pytest.mark.asyncio
async def test_hybrid_search_with_only_stopwords_still_returns_dense_results(db_session):
    vector = [1.0] + [0.0] * (EMBEDDING_DIM - 1)
    await _seed_document_with_chunk(db_session, vector, "some content")

    results = await hybrid_search(db_session, "how is it", vector, top_k=5)
    assert [r.content for r in results] == ["some content"]


# 영숫자 단어가 하나도 없는 질문('?!')은 어휘 검색을 건너뛰고 dense로 돌아간다. 한국어 질문에서 영어 API
# 이름이 없을 때도 같은 경로를 탄다.
@pytest.mark.asyncio
async def test_hybrid_search_without_searchable_words_falls_back_to_dense(db_session):
    vector = [1.0] + [0.0] * (EMBEDDING_DIM - 1)
    await _seed_document_with_chunk(db_session, vector, "some content")

    results = await hybrid_search(db_session, "?!", vector, top_k=5)
    assert [r.content for r in results] == ["some content"]


# rerank는 dense와 BM25 후보(각 목록 pool개)를 합친 뒤 재정렬기 점수만으로 순서를 정한다. dense는 일반 청크를,
# BM25는 환경 변수 청크를 가져오고, 재정렬기가 키워드 청크를 1위(점수 1.0)로 올리는지 확인한다(v6).
@pytest.mark.asyncio
async def test_rerank_search_reorders_the_union_of_dense_and_bm25_candidates(db_session):
    query_vector = [1.0] + [0.0] * (EMBEDDING_DIM - 1)
    orthogonal = [0.0] * (EMBEDDING_DIM - 1) + [1.0]
    await _seed_document_with_chunk(db_session, query_vector, "generic prose about nothing much")
    await _seed_document_with_chunk(db_session, orthogonal, "load settings from environment variables")

    # 목록마다 후보 하나: dense는 일반 문장 청크를, BM25는 environment 청크를 가져오고, 순서는 재정렬기만으로
    # 정해진다.
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


# rerank 결과도 top_k개로 자른다.
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


# pool을 주지 않으면 질문 언어의 후보 수(RERANK_POOLS: 영어 5, 한국어 3, v9)를 쓰는지 확인한다. 두 질문 모두
# 영숫자 단어가 없어 BM25 후보가 없으므로, 재정렬기가 받은 후보 수가 곧 dense 목록 길이(= pool)다.
@pytest.mark.asyncio
async def test_rerank_pool_defaults_to_the_questions_language(db_session):
    for i in range(8):
        vector = [1.0, 0.1 * i] + [0.0] * (EMBEDDING_DIM - 2)
        await _seed_document_with_chunk(db_session, vector, f"{i} english chunk", "en")
        await _seed_document_with_chunk(db_session, vector, f"{i} 한국어 청크", "ko")

    # 두 질문 모두 [A-Za-z0-9] 단어가 없으므로 후보는 dense 목록에서만 나오고, 그 길이가 정확히 후보
    # 수(pool)다.
    query_vector = [1.0] + [0.0] * (EMBEDDING_DIM - 1)
    reranker = KeywordReranker("chunk")
    await rerank_search(db_session, "?!", query_vector, 10, reranker, language="en")
    assert reranker.last_candidate_count == RERANK_POOLS["en"]
    await rerank_search(db_session, "청크를 찾아 주세요", query_vector, 10, reranker, language="ko")
    assert reranker.last_candidate_count == RERANK_POOLS["ko"]


# retrieve가 질문 언어(한글이 있으면 ko)의 청크만 찾는지, language를 직접 주면 그 언어만 찾는지 확인한다. 두
# 언어의 벡터는 다른 모델·다른 공간이라 섞어 찾으면 안 된다(v8).
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


# 지원하지 않는 언어 값은 SQL을 만들기 전에 ValueError로 막혀야 한다. 언어는 부분 인덱스를 쓰도록 SQL에
# 리터럴로 넣으므로, 검사가 없으면 SQL 주입 통로가 된다.
@pytest.mark.asyncio
async def test_unsupported_language_is_rejected_before_reaching_sql(db_session):
    vector = [1.0] + [0.0] * (EMBEDDING_DIM - 1)
    with pytest.raises(ValueError):
        await similarity_search(db_session, vector, 5, "xx'; DROP TABLE chunks; --")


# rerank 모드인데 재정렬기를 넘기지 않으면 조용히 dense로 바뀌지 않고 ValueError가 나야 한다.
@pytest.mark.asyncio
async def test_retrieve_in_rerank_mode_requires_a_reranker(db_session):
    with pytest.raises(ValueError):
        await retrieve(db_session, "q", [1.0] + [0.0] * (EMBEDDING_DIM - 1), 5, "rerank")


# --- 임베딩 모델별 점수 바닥값, 교차언어 검색 (docs/experiments.md v12) ---


# v12 테스트용 벡터 도우미: 앞 성분만 정하고 나머지는 0인 벡터, 그리고 _unit(1.0)과의 코사인이 정확히
# `cosine`인 단위 벡터.
def _unit(*components: float) -> list[float]:
    """앞쪽 성분은 주어진 값이고 나머지는 0인 벡터."""
    return list(components) + [0.0] * (EMBEDDING_DIM - len(components))


def _at_similarity(cosine: float) -> list[float]:
    """_unit(1.0)과의 코사인이 `cosine`인 단위 벡터."""
    return _unit(cosine, (1 - cosine**2) ** 0.5)


# 경로의 페이지에 청크를 하나 더한다(문서가 없으면 처음에 만든다). 언어는 경로의 docs/<언어>/에서 정한다. 같은
# 페이지의 여러 청크, 같은 페이지의 다른 번역을 만들 때 쓴다.
async def _seed_page_chunk(db_session, path: str, embedding: list[float], content: str, index: int = 0):
    """`path` 페이지의 청크 하나. 그 페이지의 문서 행은 처음 쓸 때 만든다."""
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


# dense 검색이 바닥값을 인자로 받는지 확인한다: 점수 0.25 청크는 기본 0.3에서는 잘리고 0.2에서는 나온다(모델별
# 바닥값의 바탕, v12).
@pytest.mark.asyncio
async def test_similarity_search_takes_the_score_floor_as_a_parameter(db_session):
    await _seed_page_chunk(db_session, "docs/en/docs/low.md", _at_similarity(0.25), "low score")

    assert await similarity_search(db_session, _unit(1.0), 5) == []  # 기본 바닥값 0.3 미만
    lowered = await similarity_search(db_session, _unit(1.0), 5, score_floor=0.2)
    assert [r.content for r in lowered] == ["low score"]


# SCORE_FLOORS에 없는 모델은 공통 바닥값(0.3)을 쓰고, 넣은 모델은 그 값을 쓴다(monkeypatch.setitem으로 테스트
# 뒤 되돌림).
def test_models_without_a_measured_floor_use_the_shared_one(monkeypatch):
    assert score_floor_for("intfloat/multilingual-e5-small") == SCORE_FLOOR
    monkeypatch.setitem(SCORE_FLOORS, "some/model", 0.15)
    assert score_floor_for("some/model") == 0.15


# page_key가 번역이 달라도 같은 페이지면 같은 키를 내고, docs 경로가 아니면 그대로 둔다. 평가의 페이지 단위
# Hit와 교차언어 중복 제거가 이 함수에 기댄다.
def test_page_key_is_the_same_for_every_translation_of_a_page():
    assert page_key("docs/ko/docs/tutorial/body.md") == "tutorial/body.md"
    assert page_key("docs/en/docs/tutorial/body.md") == "tutorial/body.md"
    assert page_key("docs/en/docs/index.md") == "index.md"
    assert page_key("README.md") == "README.md"  # 문서 페이지가 아니면 그대로 둔다


# 교차언어 검색은 점수순으로 합치되, 이미 다른 번역으로 들어간 페이지는 건너뛴다: a는 한국어(0.9), b는
# 영어(0.7)가 먼저 들어가 같은 내용이 두 자리를 차지하지 않는다.
@pytest.mark.asyncio
async def test_cross_lingual_search_keeps_one_translation_per_page(db_session):
    await _seed_page_chunk(db_session, "docs/ko/docs/a.md", _at_similarity(0.9), "ko a")
    await _seed_page_chunk(db_session, "docs/en/docs/a.md", _at_similarity(0.8), "en a")
    await _seed_page_chunk(db_session, "docs/en/docs/b.md", _at_similarity(0.7), "en b")
    await _seed_page_chunk(db_session, "docs/ko/docs/b.md", _at_similarity(0.6), "ko b")

    results = await cross_lingual_search(db_session, _unit(1.0), 5, ("ko", "en"))

    # 페이지 a는 한국어 청크가, 페이지 b는 영어 청크가 먼저 자리를 잡으므로, 각 페이지의 다른 번역은 같은
    # 내용을 되풀이하지 않도록 빠진다.
    assert [r.content for r in results] == ["ko a", "en b"]


# 같은 번역 안의 같은 페이지 청크 여러 개는 한 언어 검색처럼 그대로 둔다. top_k=2라 a의 두 청크가 영어 c보다
# 먼저 자리를 채운다.
@pytest.mark.asyncio
async def test_cross_lingual_search_keeps_several_chunks_of_a_page_in_one_language(db_session):
    await _seed_page_chunk(db_session, "docs/ko/docs/a.md", _at_similarity(0.9), "ko a 1", 0)
    await _seed_page_chunk(db_session, "docs/ko/docs/a.md", _at_similarity(0.8), "ko a 2", 1)
    await _seed_page_chunk(db_session, "docs/en/docs/c.md", _at_similarity(0.7), "en c")

    results = await cross_lingual_search(db_session, _unit(1.0), 2, ("ko", "en"))

    assert [r.content for r in results] == ["ko a 1", "ko a 2"]


# 바닥값은 두 언어에 똑같이 적용된다: 0.25·0.28은 기본 0.3에서 모두 잘리고, 0.2로 낮추면 둘 다 점수순으로
# 나온다.
@pytest.mark.asyncio
async def test_cross_lingual_search_applies_the_floor_to_both_languages(db_session):
    await _seed_page_chunk(db_session, "docs/ko/docs/a.md", _at_similarity(0.25), "ko a")
    await _seed_page_chunk(db_session, "docs/en/docs/b.md", _at_similarity(0.28), "en b")

    assert await cross_lingual_search(db_session, _unit(1.0), 5, ("ko", "en")) == []
    lowered = await cross_lingual_search(db_session, _unit(1.0), 5, ("ko", "en"), score_floor=0.2)
    assert [r.content for r in lowered] == ["en b", "ko a"]


# retrieve는 cross_lingual=True일 때만 다른 번역까지 찾는다. 기본은 한국어 청크만, 켜면 점수가 높은 영어
# 청크가 앞에 온다.
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


# retrieve가 받은 바닥값을 dense 검색까지 넘기는지 확인한다(평가의 --score-floor 경로).
@pytest.mark.asyncio
async def test_retrieve_passes_the_score_floor_to_dense_search(db_session):
    await _seed_page_chunk(db_session, "docs/ko/docs/a.md", _at_similarity(0.25), "ko a")

    assert await retrieve(db_session, "질문", _unit(1.0), 5, "dense", language="ko") == []
    lowered = await retrieve(
        db_session, "질문", _unit(1.0), 5, "dense", language="ko", score_floor=0.2
    )
    assert [r.content for r in lowered] == ["ko a"]


# hybrid·rerank 모드에서 질문에 영문·숫자 단어가 없으면 dense로 대신하는데, 그때도 retrieve가 받은
# 바닥값(앱에서는 임베딩 모델별 값)을 써야 한다. 예전에는 이 경로만 공통 SCORE_FLOOR(0.3)를 써서, 모델별
# 바닥값을 0.2로 두어도 점수 0.25 청크가 잘렸다.
@pytest.mark.asyncio
@pytest.mark.parametrize("mode", ["hybrid", "rerank"])
async def test_the_dense_fallback_of_hybrid_and_rerank_uses_the_given_score_floor(db_session, mode):
    await _seed_page_chunk(db_session, "docs/ko/docs/a.md", _at_similarity(0.25), "ko a")
    reranker = KeywordReranker("ko") if mode == "rerank" else None

    # "질문" has no [A-Za-z0-9] word, so both modes search with the dense list alone.
    shared = await retrieve(db_session, "질문", _unit(1.0), 5, mode, language="ko", reranker=reranker)
    lowered = await retrieve(
        db_session, "질문", _unit(1.0), 5, mode, language="ko", reranker=reranker, score_floor=0.2
    )

    assert shared == []
    assert [r.content for r in lowered] == ["ko a"]


# 교차언어 검색은 dense에만 구현돼 있으므로 hybrid와 함께 쓰면 ValueError.
@pytest.mark.asyncio
async def test_cross_lingual_retrieval_is_dense_only(db_session):
    with pytest.raises(ValueError):
        await retrieve(db_session, "질문", _unit(1.0), 5, "hybrid", language="ko", cross_lingual=True)

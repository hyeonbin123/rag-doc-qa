# [파일 역할] 질문 벡터(와 질문 글)로 같은 언어의 청크를 찾는 검색 단계. 세 가지 모드를 retrieve 하나로
# 고른다.
# - dense(기본): pgvector 코사인 거리로 가장 가까운 청크. 점수 바닥값 미만은 버린다.
# - hybrid: dense 순위와 SQL로 계산한 BM25 순위를 가중 RRF로 합친다.
# - rerank: dense 상위와 BM25 상위 후보의 합집합을 cross-encoder로 다시 채점한다.
# [설계 이유]
# - 별도 검색 엔진·확장 없이 PostgreSQL 안에서 끝낸다. BM25도 tsvector와 GIN 인덱스로 SQL에서 계산한다(README
#   'BM25를 SQL로', 이 규모에서 어휘 검색 1회 약 40~50ms).
# - 모든 검색은 한 언어 안에서만 한다. 영어·한국어 벡터는 서로 다른 모델이 만든 다른 공간이고, 언어별 부분
#   HNSW 인덱스를 쓰려면 언어를 SQL 리터럴로 넣어야 한다(_language_sql).
# - 기본 dense는 v5~v9의 미리 정한 규칙으로 확정했다. hybrid·rerank는 측정 결과 기본값이 되지 못했지만
#   설정으로 켤 수 있게 남겼다(docs/experiments.md v4~v9).
# [연결] /query/ask(app/routers/query.py)와 평가 스크립트(eval/run_retrieval_eval.py,
# eval/run_answer_eval.py)가 retrieve를 부른다.

import re
import uuid
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

# text: pgvector 거리 연산자(<=>)와 BM25 CTE를 그대로 쓰려고 ORM 대신 SQL 문을 직접 쓴다. 값은 모두 바인드
# 파라미터(:qvec 등)로 넘기고, 언어만 검사한 뒤 리터럴로 넣는다.
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

# build_embedding_text: cross-encoder에 적재 때와 같은 '헤딩 경로 + 본문'을 넣으려고 가져온다. run_model:
# 재정렬 모델을 모델 스레드에서 돌린다.
from app.services.chunking import build_embedding_text
from app.services.inference import run_model
from app.services.language import SUPPORTED_LANGUAGES, Language, detect_language

# RerankerService는 타입 힌트에만 필요해서 실행할 때는 import하지 않는다.
if TYPE_CHECKING:
    from app.services.reranking import RerankerService

RetrievalMode = Literal["dense", "hybrid", "rerank"]

# dense 점수(코사인 유사도) 바닥값. 지금 쓰는 모델은 모두 이 0.3을 쓴다(v12에서 규칙으로 정한 한국어 바닥값도
# 0.3이라 SCORE_FLOORS는 비어 있다).
SCORE_FLOOR = 0.3
# Dense results under the floor are dropped, so a question the docs don't cover gets no
# passages. Cosine scores sit in different ranges for different models, so a model whose
# on-topic scores fall lower gets its own floor, set on the Korean tuning sets only
# (docs/experiments.md v12). Models not listed use SCORE_FLOOR.
SCORE_FLOORS: dict[str, float] = {}
# RRF 상수 k. 순위 r인 결과가 가중치 / (60 + r)을 받는다. 60은 RRF에서 널리 쓰는 기본값이고 v4부터 그대로
# 썼다. k가 크면 1위와 10위의 점수 차가 작아져 한 목록의 1위가 결과를 독점하지 못한다.
RRF_K = 60
# pgvector's HNSW scan returns at most hnsw.ef_search rows (default 40), so a larger
# LIMIT would silently shrink the dense candidate list back to 40 anyway.
CANDIDATE_POOL = 40
# Standard BM25 defaults (as in Lucene/Elasticsearch), deliberately left untuned.
# k1: 단어가 반복될수록 점수가 늘다가 포화하는 정도. b: 문서 길이 정규화 강도(0이면 길이 무시, 1이면 완전
# 정규화).
BM25_K1 = 1.2
BM25_B = 0.75
# RRF weight of the BM25 list relative to the dense list (which has weight 1). Picked
# from {0.25, 0.5, 0.75, 1.0} on eval/qa_dev.jsonl only, never on the test set.
# v5 결과: 튜닝용 셋 MRR 0.953(dense 0.858)이었지만 테스트셋에서 0.894(dense 0.933)로 낮아 hybrid는 기본값이
# 되지 못했다.
LEXICAL_WEIGHT = 0.75
# Candidates taken from each of the dense and BM25 lists for the cross-encoder. Every
# candidate costs one model forward pass at query time (on a desktop CPU, about 60 ms
# each for the English MiniLM-L6 and 100 ms for the multilingual L12), so this trades
# latency for recall. Picked per language on that language's tuning set under a 1 s
# median retrieval budget: English from {5, 10, 20}, Korean from {3, 5, 8}.
# v6(영어): 목록당 5개가 튜닝용 셋 MRR 0.969, p50 627ms로 예산 안에서 가장 좋았다(10개부터 예산 초과).
# v9(한국어): 3개가 0.891, 8개는 p50 1359ms로 예산 초과. 두 목록에서 가져오므로 실제 후보는 최대 그 두
# 배(겹치면 그보다 적음)다.
RERANK_POOLS: dict[Language, int] = {"en": 5, "ko": 3}

# 질문에서 BM25에 쓸 영문·숫자 단어만 뽑는 정규식(_search_words).
_WORD_RE = re.compile(r"[A-Za-z0-9]+")
# docs/<language>/docs/<page>: every translation of a page shares <page>.
_DOCS_PATH_RE = re.compile(r"^docs/([^/]+)/docs/(.+)$")

# 아래 _BM25_CTES는 hybrid·rerank·lexical_search가 앞부분에 붙여 쓰는 공통 CTE다. 단계:
# 1) terms: 질문 단어를 content_tsv와 같은 'english' 설정으로 어간 추출한 어휘소들.
# 2) corpus: 그 언어의 청크 수 N과 평균 길이 avgdl(0으로 나누지 않게 최소 1).
# 3) idf: 어휘소마다 문서 빈도 df를 GIN 인덱스로 세고 idf = ln(1 + (N - df + 0.5) / (df + 0.5)). 1을 더한
#    형태라 흔한 단어도 음수가 되지 않는다. df가 0인 어휘소는 뺀다.
# 4) lexical: 어휘소 중 하나라도 있는 청크(어휘소를 ' | '로 이은 OR tsquery)마다 BM25 = 합(idf × tf × (k1 + 1)
#    / (tf + k1 × (1 - b + b × 길이 / avgdl)))을 계산하고, tf는 tsvector에 기록된 위치 개수로 센다. 상위
#    :pool개에 순위(rnk)를 매긴다.
# 질문 단어를 OR로 묶는 이유: plainto_tsquery처럼 AND로 묶으면 문장형 질문에는 거의 아무것도 걸리지
# 않는다(docs/experiments.md v4 구현 메모).
# BM25 over chunks.content_tsv, computed in SQL so there is no extra index or stats
# table to keep in sync with ingestion:
# - terms: the question's lexemes, stemmed with the same 'english' config as content_tsv
# - df: counted per term through the GIN index on content_tsv
# - tf: how many positions the lexeme has in the chunk's tsvector
# - length: chunks.token_count; BM25 only uses dl / avgdl, so any consistent unit works
# Postgres' own ts_rank has no IDF, which let words like "fastapi" (in 57% of chunks)
# drown out the rare, informative words of a question.
# Every statistic is taken within one language, so Korean chunks never dilute the
# English document frequencies and vice versa.
_BM25_CTES = """
    terms AS (
        SELECT lexeme FROM unnest(to_tsvector('english', :words))
    ),
    corpus AS (
        SELECT count(*)::float8 AS n, greatest(avg(token_count), 1)::float8 AS avgdl
        FROM chunks
        WHERE language = :language
    ),
    idf AS (
        SELECT t.lexeme, ln(1 + (corpus.n - df.n + 0.5) / (df.n + 0.5)) AS idf
        FROM terms t
        CROSS JOIN corpus
        CROSS JOIN LATERAL (
            SELECT count(*)::float8 AS n FROM chunks
            WHERE language = :language AND content_tsv @@ t.lexeme::tsquery
        ) df
        WHERE df.n > 0
    ),
    lexical AS (
        SELECT id, bm25, row_number() OVER (ORDER BY bm25 DESC) AS rnk
        FROM (
            SELECT c.id,
                   sum(
                       idf.idf * tf.n * (CAST(:k1 AS float8) + 1)
                       / (tf.n + CAST(:k1 AS float8)
                          * (1 - CAST(:b AS float8)
                             + CAST(:b AS float8) * c.token_count / corpus.avgdl))
                   ) AS bm25
            FROM chunks c
            CROSS JOIN corpus
            CROSS JOIN LATERAL unnest(c.content_tsv) u
            CROSS JOIN LATERAL (SELECT array_length(u.positions, 1)::float8 AS n) tf
            JOIN idf ON idf.lexeme = u.lexeme
            WHERE c.language = :language
              AND c.content_tsv @@ (SELECT string_agg(lexeme, ' | ')::tsquery FROM idf)
            GROUP BY c.id
            ORDER BY bm25 DESC
            LIMIT :pool
        ) top_lexical
    )
"""


# 검색 결과 한 건. score의 뜻은 모드마다 다르다: dense·hybrid는 코사인 유사도, rerank는 cross-encoder 관련도
# 확률, lexical_search는 BM25 점수. 생성기가 content와 heading_path로 프롬프트를 만들고, 라우터가 나머지를
# 인용·질문 기록에 쓴다.
@dataclass
class RetrievedChunk:
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    source_path: str
    heading_path: str | None
    content: str
    score: float


# 임베딩 모델별 dense 바닥값. /query/ask와 평가 스크립트가 질문을 임베딩한 모델 이름으로 부른다. 모델마다 관련
# 문서의 코사인 점수 분포가 달라 바닥값을 따로 둘 수 있게 한 것이다(위 영어 주석).
def score_floor_for(model_name: str) -> float:
    """The dense score floor for vectors from this embedding model."""
    return SCORE_FLOORS.get(model_name, SCORE_FLOOR)


# 번역이 달라도 같은 페이지면 같은 키를 돌려준다. v12부터 평가의 Hit 판정을 페이지 단위로 하는
# 데(eval/retrieval_runs.py, eval/run_answer_eval.py, eval/generator_arms.py)와 교차언어 검색의 중복 제거에
# 쓴다.
def page_key(source_path: str) -> str:
    """The page a docs path belongs to, the same for each translation of it.

    "docs/ko/docs/tutorial/body.md" and "docs/en/docs/tutorial/body.md" are both
    "tutorial/body.md". Anything else is returned unchanged.
    """
    match = _DOCS_PATH_RE.match(source_path)
    return match.group(2) if match else source_path


# 경로에서 언어 부분(docs/<언어>/docs/의 <언어>)을 꺼낸다. 형식이 다르면 빈 문자열.
def _path_language(source_path: str) -> str:
    match = _DOCS_PATH_RE.match(source_path)
    return match.group(1) if match else ""


# 질문 벡터를 pgvector 텍스트 표기 '[x1,x2,...]'로 바꿔 바인드 파라미터로 넘긴다.
def _vector_literal(query_embedding: list[float]) -> str:
    return "[" + ",".join(str(x) for x in query_embedding) + "]"


# SQL 결과 한 행을 RetrievedChunk로 바꾼다. score는 DB 숫자 타입을 파이썬 float로 맞춘다.
def _to_chunk(row) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=row.id,
        document_id=row.document_id,
        source_path=row.source_path,
        heading_path=row.heading_path,
        content=row.content,
        score=float(row.score),
    )


def _search_words(question: str) -> str:
    """Keep only the question's [A-Za-z0-9] words.

    The lexemes Postgres derives from these are plain alphanumerics, which is what
    lets the BM25 SQL cast each one straight to a tsquery without escaping. For a
    Korean question this keeps only the English API names in it (or nothing, in
    which case the lexical side is skipped).
    """
    return " ".join(_WORD_RE.findall(question))


# _BM25_CTES의 바인드 값 묶음. BM25 상위 후보 수의 기본은 CANDIDATE_POOL(40)이고, rerank는 :pool을 언어별 후보
# 수로 덮어쓴다.
def _bm25_params(words: str, language: Language) -> dict:
    return {
        "words": words,
        "language": language,
        "k1": BM25_K1,
        "b": BM25_B,
        "pool": CANDIDATE_POOL,
    }


# 언어를 SQL 문자열 리터럴로 만든다. 부분 인덱스(WHERE language = 'en')는 질의의 WHERE가 그 조건과 글자 그대로
# 맞아야 플래너가 쓸 수 있어서 바인드 파라미터 대신 리터럴을 넣는다. 지원 언어 목록으로 먼저 검사하므로 SQL
# 주입 위험이 없다.
def _language_sql(language: Language) -> str:
    """The language as an SQL literal, for the vector queries.

    Each language has its own partial HNSW index (migration 0004). The planner only
    uses a partial index when the WHERE clause matches its predicate as written, which
    a bind parameter can't guarantee, so the value is inlined, after checking it
    against the fixed list of supported languages.
    """
    if language not in SUPPORTED_LANGUAGES:
        raise ValueError(f"unsupported docs language {language!r}")
    return f"'{language}'"


# dense 검색 SQL. ORDER BY 거리 + LIMIT 형태라 그 언어의 HNSW 인덱스로 근사 최근접 탐색을 할 수 있다. 1 -
# 코사인 거리 = 코사인 유사도를 score로 돌려준다. 평가의 실행 계획 확인(eval/retrieval_checks.py)도 이 함수로
# 앱과 똑같은 SQL을 EXPLAIN한다.
def dense_search_sql(language: Language) -> str:
    """The dense search statement for one language (binds :qvec and :top_k)."""
    return f"""
        SELECT c.id, c.document_id, c.content, c.heading_path, d.source_path,
               1 - (c.embedding <=> :qvec) AS score
        FROM chunks c
        JOIN documents d ON d.id = c.document_id
        WHERE c.language = {_language_sql(language)}
        ORDER BY c.embedding <=> :qvec
        LIMIT :top_k
    """


# dense 검색. 상위 top_k를 가져온 뒤 바닥값 미만을 버리므로 top_k보다 적게(0개도) 돌려줄 수 있다. 문서가
# 다루지 않는 질문에는 근거가 없게 하려는 것이다. 임베딩이 정규화돼 있어 점수는 대략 0~1이다.
async def similarity_search(
    db: AsyncSession,
    query_embedding: list[float],
    top_k: int,
    language: Language = "en",
    score_floor: float = SCORE_FLOOR,
) -> list[RetrievedChunk]:
    """Cosine similarity search over chunks via pgvector's <=> operator.

    `1 - (embedding <=> :qvec)` converts cosine *distance* into a
    similarity score in roughly [0, 1] for normalized vectors. Of the top_k, the ones
    scoring under `score_floor` are dropped.
    """
    result = await db.execute(
        text(dense_search_sql(language)),
        {"qvec": _vector_literal(query_embedding), "top_k": top_k},
    )
    chunks = [_to_chunk(row) for row in result]
    return [c for c in chunks if c.score >= score_floor]


# 여러 번역을 한꺼번에 검색하는 dense 검색(v12의 T3). 같은 다국어 모델로 모든 언어를 임베딩한 경우에만 점수를
# 합칠 수 있다. v12에서 튜닝용 셋에서 이득이 없어 앱에서는 쓰지 않고, 평가가 retrieve(cross_lingual=True)로만
# 부른다.
# 언어마다 2 × top_k를 뽑아 점수순으로 합치고, 같은 페이지가 이미 다른 번역으로 들어 있으면 건너뛴다(같은
# 내용이 자리를 두 번 차지하지 않게).
async def cross_lingual_search(
    db: AsyncSession,
    query_embedding: list[float],
    top_k: int,
    languages: tuple[Language, ...],
    score_floor: float = SCORE_FLOOR,
) -> list[RetrievedChunk]:
    """Dense search over several translations at once, one translation per page.

    Only meaningful when every searched language was embedded by the same multilingual
    model as the question (docs/experiments.md v12, "T3"): the scores are then on one
    scale and can be merged. Each language's top 2 * top_k (through its own HNSW index)
    are merged by score. A chunk is skipped when its page is already in the list in
    another translation, so the same content does not take two of the top_k places;
    several chunks of one page in the same translation are kept, as in a one-language
    search.
    """
    candidates: list[RetrievedChunk] = []
    for language in languages:
        candidates += await similarity_search(
            db, query_embedding, 2 * top_k, language, score_floor
        )
    candidates.sort(key=lambda c: c.score, reverse=True)

    page_language: dict[str, str] = {}
    merged: list[RetrievedChunk] = []
    for chunk in candidates:
        language = _path_language(chunk.source_path)
        if page_language.setdefault(page_key(chunk.source_path), language) != language:
            continue
        merged.append(chunk)
        if len(merged) == top_k:
            break
    return merged


# BM25만으로 순위를 매긴다. 앱의 검색 경로에서는 부르지 않고, 테스트(tests/test_retrieval.py)가 드문 단어가
# 반복된 흔한 단어보다 높게 평가되는지 확인하는 데 쓴다. 질문에 영문·숫자 단어가 없으면 빈 목록.
async def lexical_search(
    db: AsyncSession, question: str, top_k: int, language: Language = "en"
) -> list[RetrievedChunk]:
    """BM25-only ranking, the lexical half of hybrid_search. `score` is the BM25 score."""
    words = _search_words(question)
    if not words:
        return []

    result = await db.execute(
        text(
            f"""
            WITH {_BM25_CTES}
            SELECT c.id, c.document_id, c.content, c.heading_path, d.source_path,
                   l.bm25 AS score
            FROM lexical l
            JOIN chunks c ON c.id = l.id
            JOIN documents d ON d.id = c.document_id
            ORDER BY l.rnk
            LIMIT :top_k
            """
        ),
        {**_bm25_params(words, language), "top_k": top_k},
    )
    return [_to_chunk(row) for row in result]


# dense 상위 40개와 BM25 상위 40개를 가중 RRF로 합친다. 한 SQL 안에서 두 순위를 만들고 id별로 가중치 / (60 +
# 순위)를 더해 정렬한다.
# 배경: v4는 ts_rank(IDF 없음)로 테스트셋 MRR이 0.933 → 0.898로 떨어졌고, v5에서 BM25로 바꿔도 테스트셋에서
# dense보다 낮아 기본값이 되지 못했다. RRF는 두 목록이 함께 올린 결과를 한 목록만 1위로 올린 결과보다 높게
# 치는 구조라, BM25로만 찾히는 정답(q017)이 밀리는 한계도 v5에서 확인했다.
# 질문에 영문·숫자 단어가 없으면(예: 한글만 있는 질문) dense 검색으로 대신하고, 그때는 받은 바닥값
# score_floor(임베딩 모델별 값)를 dense 검색처럼 적용한다.
async def hybrid_search(
    db: AsyncSession,
    question: str,
    query_embedding: list[float],
    top_k: int,
    lexical_weight: float = LEXICAL_WEIGHT,
    language: Language = "en",
    score_floor: float = SCORE_FLOOR,
) -> list[RetrievedChunk]:
    """Fuse the dense and BM25 rankings with weighted Reciprocal Rank Fusion.

    Each ranked list contributes weight / (RRF_K + rank); ranks are fused rather than
    raw scores because cosine similarity and BM25 live on unrelated scales. `score`
    stays the cosine similarity so it means the same thing in both modes.
    SCORE_FLOOR is not applied: a passage that only matched lexically can have a low
    cosine score, and surfacing exactly those passages is the point of this mode. A
    question with no searchable words falls back to dense search, under `score_floor`.
    """
    words = _search_words(question)
    if not words:
        return await similarity_search(db, query_embedding, top_k, language, score_floor)

    result = await db.execute(
        text(
            f"""
            WITH {_BM25_CTES},
            dense AS (
                SELECT id, row_number() OVER (ORDER BY dist) AS rnk
                FROM (
                    SELECT id, embedding <=> :qvec AS dist
                    FROM chunks
                    WHERE language = {_language_sql(language)}
                    ORDER BY dist
                    LIMIT :pool
                ) top_dense
            ),
            fused AS (
                SELECT id, sum(weight / (:rrf_k + rnk)) AS rrf
                FROM (
                    SELECT id, rnk, 1.0 AS weight FROM dense
                    UNION ALL
                    SELECT id, rnk, CAST(:lexical_weight AS float8) FROM lexical
                ) ranked
                GROUP BY id
            )
            SELECT c.id, c.document_id, c.content, c.heading_path, d.source_path,
                   1 - (c.embedding <=> :qvec) AS score
            FROM fused f
            JOIN chunks c ON c.id = f.id
            JOIN documents d ON d.id = c.document_id
            ORDER BY f.rrf DESC
            LIMIT :top_k
            """
        ),
        {
            **_bm25_params(words, language),
            "qvec": _vector_literal(query_embedding),
            "rrf_k": RRF_K,
            "lexical_weight": lexical_weight,
            "top_k": top_k,
        },
    )
    return [_to_chunk(row) for row in result]


# 재정렬 후보: dense 상위 pool개와 BM25 상위 pool개의 합집합(UNION이라 겹치면 한 번만). 순서는 의미 없고
# score는 일단 코사인 유사도다. 영문·숫자 단어가 없으면 dense 후보만 쓰고, 그때는 받은 바닥값
# score_floor(임베딩 모델별 값)를 적용한다.
async def _rerank_candidates(
    db: AsyncSession,
    question: str,
    query_embedding: list[float],
    pool: int,
    language: Language,
    score_floor: float = SCORE_FLOOR,
) -> list[RetrievedChunk]:
    """The union of the dense top `pool` and the BM25 top `pool`, in no particular order."""
    words = _search_words(question)
    if not words:
        return await similarity_search(db, query_embedding, pool, language, score_floor)

    result = await db.execute(
        text(
            f"""
            WITH {_BM25_CTES},
            dense AS (
                SELECT id FROM chunks
                WHERE language = {_language_sql(language)}
                ORDER BY embedding <=> :qvec
                LIMIT :pool
            ),
            candidates AS (
                SELECT id FROM dense UNION SELECT id FROM lexical
            )
            SELECT c.id, c.document_id, c.content, c.heading_path, d.source_path,
                   1 - (c.embedding <=> :qvec) AS score
            FROM candidates k
            JOIN chunks c ON c.id = k.id
            JOIN documents d ON d.id = c.document_id
            """
        ),
        {
            **_bm25_params(words, language),
            "pool": pool,
            "qvec": _vector_literal(query_embedding),
        },
    )
    return [_to_chunk(row) for row in result]


# 후보를 cross-encoder로 다시 채점해 상위 top_k를 돌려준다. v5에서 RRF 구조 때문에 BM25 1위 정답이 밀리는 것을
# 보고 v6에서 추가했다. 후보 하나마다 모델을 한 번 돌리므로 언어별 후보 수(RERANK_POOLS)를 지연 예산 안에서
# 골랐다.
# 결과: 영어 v7 새 테스트셋에서 Hit@5는 0.88 → 0.93으로 올랐지만 답변 정확도가 4.60으로 동점이라 기본값은
# dense를 유지했다. 한국어 v9도 Hit@5 하락으로 탈락했다.
async def rerank_search(
    db: AsyncSession,
    question: str,
    query_embedding: list[float],
    top_k: int,
    reranker: "RerankerService",
    pool: int | None = None,
    language: Language = "en",
    score_floor: float = SCORE_FLOOR,
) -> list[RetrievedChunk]:
    """Re-score the union of the dense and BM25 candidates with a cross-encoder.

    Unlike RRF, a candidate that only one list found is judged on its own text rather
    than on how many lists agreed on it. `score` becomes the reranker's relevance
    probability. `pool` defaults to the language's RERANK_POOLS entry. `score_floor` applies
    when the question has no searchable words and the candidates are dense only.
    """
    # pool을 주지 않으면(평가의 --rerank-pool 생략, 앱) 질문 언어의 기본 후보 수를 쓴다. 후보마다
    # cross-encoder 입력은 적재 임베딩과 같은 '헤딩 경로 + 본문' 형식이다.
    pool = pool or RERANK_POOLS[language]
    candidates = await _rerank_candidates(db, question, query_embedding, pool, language, score_floor)
    passages = [build_embedding_text(c.heading_path or "", c.content) for c in candidates]
    # The model call is CPU-bound; the model thread keeps the event loop free meanwhile.
    scores = await run_model(reranker.score, question, passages)
    # 각 후보의 score를 재정렬 점수로 바꾸고 높은 순으로 정렬해 top_k만 남긴다.
    for chunk, score in zip(candidates, scores, strict=True):
        chunk.score = score
    candidates.sort(key=lambda c: c.score, reverse=True)
    return candidates[:top_k]


# 검색 진입점. 언어를 정하고(없으면 질문에서 판별) 모드에 맞는 함수로 보낸다.
# - cross_lingual은 dense에서만 허용하고 평가 전용이다.
# - rerank 모드인데 재정렬 모델이 없으면 설정 오류이므로 바로 예외를 낸다.
# - 바닥값(score_floor)은 dense 검색에 쓴다. hybrid·rerank는 docstring처럼 어휘로만 걸린 낮은 코사인 점수의
#   청크를 살리는 것이 목적이라 바닥값을 쓰지 않지만, 질문에 영문·숫자 단어가 없어 dense로 대신할 때는 같은
#   바닥값을 쓴다. 예전에는 이 대신 경로만 모델별 바닥값이 아닌 공통 SCORE_FLOOR를 썼다(SCORE_FLOORS가
#   비어 있는 동안은 같은 값).
async def retrieve(
    db: AsyncSession,
    question: str,
    query_embedding: list[float],
    top_k: int,
    mode: RetrievalMode,
    *,
    language: Language | None = None,
    lexical_weight: float = LEXICAL_WEIGHT,
    reranker: "RerankerService | None" = None,
    rerank_pool: int | None = None,
    score_floor: float = SCORE_FLOOR,
    cross_lingual: bool = False,
) -> list[RetrievedChunk]:
    """Search the docs translation matching `language`, detected from the question if None.

    `score_floor` applies to dense search, including the dense fallback of the hybrid and
    rerank modes for a question with no searchable words. `cross_lingual` (dense only) searches every
    translation instead, the question's own first; see cross_lingual_search.
    """
    language = language or detect_language(question)
    if cross_lingual:
        if mode != "dense":
            raise ValueError("cross-lingual retrieval is dense only")
        others = tuple(lang for lang in SUPPORTED_LANGUAGES if lang != language)
        return await cross_lingual_search(
            db, query_embedding, top_k, (language, *others), score_floor
        )
    if mode == "rerank":
        if reranker is None:
            raise ValueError("retrieval mode 'rerank' needs a reranker")
        return await rerank_search(
            db, question, query_embedding, top_k, reranker, rerank_pool, language, score_floor
        )
    if mode == "hybrid":
        return await hybrid_search(
            db, question, query_embedding, top_k, lexical_weight, language, score_floor
        )
    return await similarity_search(db, query_embedding, top_k, language, score_floor)

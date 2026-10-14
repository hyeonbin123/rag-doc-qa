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
# 바닥값 미만의 dense 결과는 버리므로, 문서가 다루지 않는 질문에는 근거 청크가 붙지 않는다. 코사인 점수가
# 놓이는 범위는 모델마다 달라서, 관련 문서의 점수가 더 낮게 나오는 모델에는 따로 바닥값을 둘 수 있다. 그 값은
# 한국어 튜닝용 셋에서만 정한다(docs/experiments.md v12). 여기 없는 모델은 SCORE_FLOOR를 쓴다.
SCORE_FLOORS: dict[str, float] = {}
# RRF 상수 k. 순위 r인 결과가 가중치 / (60 + r)을 받는다. 60은 RRF에서 널리 쓰는 기본값이고 v4부터 그대로
# 썼다. k가 크면 1위와 10위의 점수 차가 작아져 한 목록의 1위가 결과를 독점하지 못한다.
RRF_K = 60
# pgvector의 HNSW 탐색은 최대 hnsw.ef_search개(기본 40) 행만 돌려준다. LIMIT을 더 크게 잡아도 dense 후보
# 목록은 어차피 조용히 40개로 줄어든다.
CANDIDATE_POOL = 40
# 표준 BM25 기본값(Lucene·Elasticsearch와 같음). 일부러 튜닝하지 않았다.
# k1: 단어가 반복될수록 점수가 늘다가 포화하는 정도. b: 문서 길이 정규화 강도(0이면 길이 무시, 1이면 완전
# 정규화).
BM25_K1 = 1.2
BM25_B = 0.75
# dense 목록(가중치 1)에 대한 BM25 목록의 RRF 가중치. {0.25, 0.5, 0.75, 1.0} 중에서 eval/qa_dev.jsonl로만
# 골랐고, 테스트셋으로는 고르지 않았다.
# v5 결과: 튜닝용 셋 MRR 0.953(dense 0.858)이었지만 테스트셋에서 0.894(dense 0.933)로 낮아 hybrid는 기본값이
# 되지 못했다.
LEXICAL_WEIGHT = 0.75
# cross-encoder에 넘길 후보를 dense 목록과 BM25 목록에서 각각 몇 개씩 가져올지. 후보 하나마다 질의 시점에
# 모델 forward를 한 번 돌려야 해서(데스크톱 CPU에서 영어 MiniLM-L6은 약 60ms, 다국어 L12는 약 100ms) 지연과
# 재현율을 맞바꾸는 값이다. 언어마다 그 언어의 튜닝용 셋에서, 검색 지연 중앙값 1초 예산 안에서 골랐다:
# 영어는 {5, 10, 20}, 한국어는 {3, 5, 8} 중에서.
# v6(영어): 목록당 5개가 튜닝용 셋 MRR 0.969, p50 627ms로 예산 안에서 가장 좋았다(10개부터 예산 초과).
# v9(한국어): 3개가 0.891, 8개는 p50 1359ms로 예산 초과. 두 목록에서 가져오므로 실제 후보는 최대 그 두
# 배(겹치면 그보다 적음)다.
RERANK_POOLS: dict[Language, int] = {"en": 5, "ko": 3}

# 질문에서 BM25에 쓸 영문·숫자 단어만 뽑는 정규식(_search_words).
_WORD_RE = re.compile(r"[A-Za-z0-9]+")
# docs/<언어>/docs/<페이지> 형태의 경로. 한 페이지의 모든 번역은 같은 <페이지> 부분을 갖는다.
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
# chunks.content_tsv 위의 BM25를 SQL로 계산하므로, 적재와 맞춰 둘 별도 인덱스나 통계 테이블이 필요 없다.
# - 길이: chunks.token_count. BM25는 dl / avgdl 비율만 쓰므로 단위가 일정하기만 하면 된다.
# Postgres 자체의 ts_rank에는 IDF가 없어서, "fastapi"처럼 흔한 단어(청크의 57%에 있음)가 질문의 드물고 정보가
# 많은 단어를 묻어 버렸다(v4가 채택되지 못한 원인).
# 모든 통계는 한 언어 안에서만 계산하므로, 한국어 청크가 영어 문서 빈도를 흐리지 않고 그 반대도 마찬가지다.
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
# 문서의 코사인 점수 분포가 달라 바닥값을 따로 둘 수 있게 한 것이다(위 SCORE_FLOORS 주석).
def score_floor_for(model_name: str) -> float:
    """이 임베딩 모델이 만든 벡터에 쓰는 dense 점수 바닥값."""
    return SCORE_FLOORS.get(model_name, SCORE_FLOOR)


# 번역이 달라도 같은 페이지면 같은 키를 돌려준다. v12부터 평가의 Hit 판정을 페이지 단위로 하는
# 데(eval/retrieval_runs.py, eval/run_answer_eval.py, eval/generator_arms.py)와 교차언어 검색의 중복 제거에
# 쓴다.
def page_key(source_path: str) -> str:
    """문서 경로가 속한 페이지. 한 페이지의 모든 번역이 같은 값을 갖는다.

    "docs/ko/docs/tutorial/body.md"와 "docs/en/docs/tutorial/body.md"는 둘 다 "tutorial/body.md"다.
    이 형식이 아닌 경로는 그대로 돌려준다.
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
    """질문에서 [A-Za-z0-9] 단어만 남긴다.

    여기서 Postgres가 만드는 어휘소는 평범한 영문·숫자뿐이라, BM25 SQL이 이스케이프 없이 각 어휘소를 바로
    tsquery로 바꿀 수 있다. 한국어 질문이면 그 안의 영어 API 이름만 남는다(하나도 없으면 어휘 검색 쪽을
    건너뛴다).
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
    """벡터 질의에 넣을 SQL 리터럴 형태의 언어 값.

    언어마다 부분 HNSW 인덱스가 따로 있다(마이그레이션 0004). 플래너는 WHERE 절이 인덱스 조건과 쓰인 그대로
    맞을 때만 부분 인덱스를 쓰는데, 바인드 파라미터로는 이를 보장할 수 없다. 그래서 정해진 지원 언어
    목록으로 값을 검사한 뒤 SQL에 직접 넣는다.
    """
    if language not in SUPPORTED_LANGUAGES:
        raise ValueError(f"unsupported docs language {language!r}")
    return f"'{language}'"


# dense 검색 SQL. ORDER BY 거리 + LIMIT 형태라 그 언어의 HNSW 인덱스로 근사 최근접 탐색을 할 수 있다. 1 -
# 코사인 거리 = 코사인 유사도를 score로 돌려준다. 평가의 실행 계획 확인(eval/retrieval_checks.py)도 이 함수로
# 앱과 똑같은 SQL을 EXPLAIN한다.
def dense_search_sql(language: Language) -> str:
    """한 언어의 dense 검색 SQL 문(바인드 값은 :qvec와 :top_k)."""
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
    """pgvector의 <=> 연산자로 청크를 코사인 유사도 검색한다.

    `1 - (embedding <=> :qvec)`는 코사인 *거리*를 유사도 점수로 바꾸며, 정규화된 벡터라면 대략 [0, 1]
    범위다. 상위 top_k개 중 `score_floor` 미만인 것은 버린다.
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
    """여러 번역을 한꺼번에 dense 검색하되, 한 페이지는 한 번역만 남긴다.

    검색하는 모든 언어를 질문과 같은 다국어 모델로 임베딩했을 때만 의미가 있다(docs/experiments.md v12,
    "T3"). 그래야 점수가 한 척도 위에 있어 합칠 수 있다. 언어마다 (그 언어의 HNSW 인덱스로) 상위
    2 * top_k개를 뽑아 점수순으로 합친다. 어떤 청크의 페이지가 다른 번역으로 이미 목록에 있으면 그 청크는
    건너뛰어, 같은 내용이 top_k 자리를 두 번 차지하지 않게 한다. 같은 번역 안에서 한 페이지의 청크가 여러
    개인 것은 한 언어 검색과 마찬가지로 그대로 둔다.
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
    """BM25만으로 매긴 순위. hybrid_search의 어휘 검색 절반이다. `score`는 BM25 점수."""
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
    """dense 순위와 BM25 순위를 가중 RRF(Reciprocal Rank Fusion)로 합친다.

    순위 목록마다 가중치 / (RRF_K + 순위)를 더한다. 코사인 유사도와 BM25는 서로 무관한 척도라 날것의
    점수가 아니라 순위를 합친다. `score`는 코사인 유사도로 두어 두 모드에서 같은 뜻을 갖게 한다.
    SCORE_FLOOR는 적용하지 않는다: 어휘로만 걸린 문서 조각은 코사인 점수가 낮을 수 있는데, 바로 그런 조각을
    끌어올리는 것이 이 모드의 목적이기 때문이다. 검색할 단어가 없는 질문은 dense 검색으로 대신하고, 그때는
    `score_floor`를 적용한다.
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
    """dense 상위 `pool`개와 BM25 상위 `pool`개의 합집합. 순서는 정해져 있지 않다."""
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
    """dense 후보와 BM25 후보의 합집합을 cross-encoder로 다시 채점한다.

    RRF와 달리, 한 목록에서만 찾은 후보도 몇 개의 목록이 동의했는지가 아니라 자기 글 내용으로 평가받는다.
    `score`는 재정렬 모델의 관련도 확률이 된다. `pool`의 기본값은 그 언어의 RERANK_POOLS 값이다.
    `score_floor`는 질문에 검색할 단어가 없어 후보가 dense 결과뿐일 때 적용한다.
    """
    # pool을 주지 않으면(평가의 --rerank-pool 생략, 앱) 질문 언어의 기본 후보 수를 쓴다. 후보마다
    # cross-encoder 입력은 적재 임베딩과 같은 '헤딩 경로 + 본문' 형식이다.
    pool = pool or RERANK_POOLS[language]
    candidates = await _rerank_candidates(db, question, query_embedding, pool, language, score_floor)
    passages = [build_embedding_text(c.heading_path or "", c.content) for c in candidates]
    # 모델 호출은 CPU를 쓰므로 모델 스레드에서 돌려, 그동안 이벤트 루프가 다른 일을 하게 둔다.
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
    """`language`에 맞는 번역 문서를 검색한다. None이면 질문에서 언어를 판별한다.

    `score_floor`는 dense 검색에 적용되며, 검색할 단어가 없는 질문에서 hybrid·rerank 모드가 dense로
    대신하는 경우도 포함한다. `cross_lingual`(dense 전용)이면 질문 언어를 먼저 두고 모든 번역을 함께
    검색한다. cross_lingual_search 참고.
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

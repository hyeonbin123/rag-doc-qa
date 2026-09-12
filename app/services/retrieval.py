import asyncio
import re
import uuid
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.chunking import build_embedding_text
from app.services.language import SUPPORTED_LANGUAGES, Language, detect_language

if TYPE_CHECKING:
    from app.services.reranking import RerankerService

RetrievalMode = Literal["dense", "hybrid", "rerank"]

SCORE_FLOOR = 0.3
RRF_K = 60
# pgvector's HNSW scan returns at most hnsw.ef_search rows (default 40), so a larger
# LIMIT would silently shrink the dense candidate list back to 40 anyway.
CANDIDATE_POOL = 40
# Standard BM25 defaults (as in Lucene/Elasticsearch), deliberately left untuned.
BM25_K1 = 1.2
BM25_B = 0.75
# RRF weight of the BM25 list relative to the dense list (which has weight 1). Picked
# from {0.25, 0.5, 0.75, 1.0} on eval/qa_dev.jsonl only, never on the test set.
LEXICAL_WEIGHT = 0.75
# Candidates taken from each of the dense and BM25 lists for the cross-encoder. Every
# candidate costs one model forward pass at query time (on a desktop CPU, about 60 ms
# each for the English MiniLM-L6 and 100 ms for the multilingual L12), so this trades
# latency for recall. Picked per language on that language's tuning set under a 1 s
# median retrieval budget: English from {5, 10, 20}, Korean from {3, 5, 8}.
RERANK_POOLS: dict[Language, int] = {"en": 5, "ko": 3}

_WORD_RE = re.compile(r"[A-Za-z0-9]+")

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


@dataclass
class RetrievedChunk:
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    source_path: str
    heading_path: str | None
    content: str
    score: float


def _vector_literal(query_embedding: list[float]) -> str:
    return "[" + ",".join(str(x) for x in query_embedding) + "]"


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


def _bm25_params(words: str, language: Language) -> dict:
    return {
        "words": words,
        "language": language,
        "k1": BM25_K1,
        "b": BM25_B,
        "pool": CANDIDATE_POOL,
    }


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


async def similarity_search(
    db: AsyncSession, query_embedding: list[float], top_k: int, language: Language = "en"
) -> list[RetrievedChunk]:
    """Cosine similarity search over chunks via pgvector's <=> operator.

    `1 - (embedding <=> :qvec)` converts cosine *distance* into a
    similarity score in roughly [0, 1] for normalized vectors.
    """
    result = await db.execute(
        text(
            f"""
            SELECT c.id, c.document_id, c.content, c.heading_path, d.source_path,
                   1 - (c.embedding <=> :qvec) AS score
            FROM chunks c
            JOIN documents d ON d.id = c.document_id
            WHERE c.language = {_language_sql(language)}
            ORDER BY c.embedding <=> :qvec
            LIMIT :top_k
            """
        ),
        {"qvec": _vector_literal(query_embedding), "top_k": top_k},
    )
    chunks = [_to_chunk(row) for row in result]
    return [c for c in chunks if c.score >= SCORE_FLOOR]


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


async def hybrid_search(
    db: AsyncSession,
    question: str,
    query_embedding: list[float],
    top_k: int,
    lexical_weight: float = LEXICAL_WEIGHT,
    language: Language = "en",
) -> list[RetrievedChunk]:
    """Fuse the dense and BM25 rankings with weighted Reciprocal Rank Fusion.

    Each ranked list contributes weight / (RRF_K + rank); ranks are fused rather than
    raw scores because cosine similarity and BM25 live on unrelated scales. `score`
    stays the cosine similarity so it means the same thing in both modes.
    SCORE_FLOOR is not applied: a passage that only matched lexically can have a low
    cosine score, and surfacing exactly those passages is the point of this mode.
    """
    words = _search_words(question)
    if not words:
        return await similarity_search(db, query_embedding, top_k, language)

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


async def _rerank_candidates(
    db: AsyncSession, question: str, query_embedding: list[float], pool: int, language: Language
) -> list[RetrievedChunk]:
    """The union of the dense top `pool` and the BM25 top `pool`, in no particular order."""
    words = _search_words(question)
    if not words:
        return await similarity_search(db, query_embedding, pool, language)

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


async def rerank_search(
    db: AsyncSession,
    question: str,
    query_embedding: list[float],
    top_k: int,
    reranker: "RerankerService",
    pool: int | None = None,
    language: Language = "en",
) -> list[RetrievedChunk]:
    """Re-score the union of the dense and BM25 candidates with a cross-encoder.

    Unlike RRF, a candidate that only one list found is judged on its own text rather
    than on how many lists agreed on it. `score` becomes the reranker's relevance
    probability. `pool` defaults to the language's RERANK_POOLS entry.
    """
    pool = pool or RERANK_POOLS[language]
    candidates = await _rerank_candidates(db, question, query_embedding, pool, language)
    passages = [build_embedding_text(c.heading_path or "", c.content) for c in candidates]
    # The model call is CPU-bound; a worker thread keeps the event loop free meanwhile.
    scores = await asyncio.to_thread(reranker.score, question, passages)
    for chunk, score in zip(candidates, scores, strict=True):
        chunk.score = score
    candidates.sort(key=lambda c: c.score, reverse=True)
    return candidates[:top_k]


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
) -> list[RetrievedChunk]:
    """Search the docs translation matching `language`, detected from the question if None."""
    language = language or detect_language(question)
    if mode == "rerank":
        if reranker is None:
            raise ValueError("retrieval mode 'rerank' needs a reranker")
        return await rerank_search(
            db, question, query_embedding, top_k, reranker, rerank_pool, language
        )
    if mode == "hybrid":
        return await hybrid_search(
            db, question, query_embedding, top_k, lexical_weight, language
        )
    return await similarity_search(db, query_embedding, top_k, language)

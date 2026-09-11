import re
import uuid
from dataclasses import dataclass
from typing import Literal

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

RetrievalMode = Literal["dense", "hybrid"]

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

_WORD_RE = re.compile(r"[A-Za-z0-9]+")

# BM25 over chunks.content_tsv, computed in SQL so there is no extra index or stats
# table to keep in sync with ingestion:
# - terms: the question's lexemes, stemmed with the same 'english' config as content_tsv
# - df: counted per term through the GIN index on content_tsv
# - tf: how many positions the lexeme has in the chunk's tsvector
# - length: chunks.token_count; BM25 only uses dl / avgdl, so any consistent unit works
# Postgres' own ts_rank has no IDF, which let words like "fastapi" (in 57% of chunks)
# drown out the rare, informative words of a question.
_BM25_CTES = """
    terms AS (
        SELECT lexeme FROM unnest(to_tsvector('english', :words))
    ),
    corpus AS (
        SELECT count(*)::float8 AS n, greatest(avg(token_count), 1)::float8 AS avgdl
        FROM chunks
    ),
    idf AS (
        SELECT t.lexeme, ln(1 + (corpus.n - df.n + 0.5) / (df.n + 0.5)) AS idf
        FROM terms t
        CROSS JOIN corpus
        CROSS JOIN LATERAL (
            SELECT count(*)::float8 AS n FROM chunks WHERE content_tsv @@ t.lexeme::tsquery
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
            WHERE c.content_tsv @@ (SELECT string_agg(lexeme, ' | ')::tsquery FROM idf)
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
    lets the BM25 SQL cast each one straight to a tsquery without escaping.
    """
    return " ".join(_WORD_RE.findall(question))


def _bm25_params(words: str) -> dict:
    return {"words": words, "k1": BM25_K1, "b": BM25_B, "pool": CANDIDATE_POOL}


async def similarity_search(
    db: AsyncSession, query_embedding: list[float], top_k: int
) -> list[RetrievedChunk]:
    """Cosine similarity search over chunks via pgvector's <=> operator.

    `1 - (embedding <=> :qvec)` converts cosine *distance* into a
    similarity score in roughly [0, 1] for normalized vectors.
    """
    result = await db.execute(
        text(
            """
            SELECT c.id, c.document_id, c.content, c.heading_path, d.source_path,
                   1 - (c.embedding <=> :qvec) AS score
            FROM chunks c
            JOIN documents d ON d.id = c.document_id
            ORDER BY c.embedding <=> :qvec
            LIMIT :top_k
            """
        ),
        {"qvec": _vector_literal(query_embedding), "top_k": top_k},
    )
    chunks = [_to_chunk(row) for row in result]
    return [c for c in chunks if c.score >= SCORE_FLOOR]


async def lexical_search(db: AsyncSession, question: str, top_k: int) -> list[RetrievedChunk]:
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
        {**_bm25_params(words), "top_k": top_k},
    )
    return [_to_chunk(row) for row in result]


async def hybrid_search(
    db: AsyncSession,
    question: str,
    query_embedding: list[float],
    top_k: int,
    lexical_weight: float = LEXICAL_WEIGHT,
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
        return await similarity_search(db, query_embedding, top_k)

    result = await db.execute(
        text(
            f"""
            WITH {_BM25_CTES},
            dense AS (
                SELECT id, row_number() OVER (ORDER BY dist) AS rnk
                FROM (
                    SELECT id, embedding <=> :qvec AS dist
                    FROM chunks
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
            **_bm25_params(words),
            "qvec": _vector_literal(query_embedding),
            "rrf_k": RRF_K,
            "lexical_weight": lexical_weight,
            "top_k": top_k,
        },
    )
    return [_to_chunk(row) for row in result]


async def retrieve(
    db: AsyncSession,
    question: str,
    query_embedding: list[float],
    top_k: int,
    mode: RetrievalMode,
    lexical_weight: float = LEXICAL_WEIGHT,
) -> list[RetrievedChunk]:
    if mode == "hybrid":
        return await hybrid_search(db, question, query_embedding, top_k, lexical_weight)
    return await similarity_search(db, query_embedding, top_k)

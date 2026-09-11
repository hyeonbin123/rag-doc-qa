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

_WORD_RE = re.compile(r"[A-Za-z0-9]+")


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


def _any_word_query(question: str) -> str:
    """OR together the question's words for to_tsquery.

    plainto_tsquery/websearch_to_tsquery AND every term, which for a full-sentence
    question matches almost nothing. Keeping only [A-Za-z0-9] tokens guarantees the
    string contains no tsquery operators.
    """
    return " | ".join(_WORD_RE.findall(question))


async def hybrid_search(
    db: AsyncSession, question: str, query_embedding: list[float], top_k: int
) -> list[RetrievedChunk]:
    """Fuse dense and full-text rankings with Reciprocal Rank Fusion.

    Each ranked list contributes 1 / (RRF_K + rank); ranks are fused rather than raw
    scores because cosine similarity and ts_rank live on unrelated scales. `score`
    stays the cosine similarity so it means the same thing in both modes.
    SCORE_FLOOR is not applied: a passage that only matched lexically can have a low
    cosine score, and surfacing exactly those passages is the point of this mode.
    """
    word_query = _any_word_query(question)
    if not word_query:
        return await similarity_search(db, query_embedding, top_k)

    result = await db.execute(
        text(
            """
            WITH q AS (SELECT to_tsquery('english', :word_query) AS query),
            dense AS (
                SELECT id, row_number() OVER (ORDER BY dist) AS rnk
                FROM (
                    SELECT id, embedding <=> :qvec AS dist
                    FROM chunks
                    ORDER BY dist
                    LIMIT :pool
                ) top_dense
            ),
            lexical AS (
                SELECT id, row_number() OVER (ORDER BY rank DESC) AS rnk
                FROM (
                    SELECT c.id, ts_rank(c.content_tsv, q.query) AS rank
                    FROM chunks c, q
                    WHERE c.content_tsv @@ q.query
                    ORDER BY rank DESC
                    LIMIT :pool
                ) top_lexical
            ),
            fused AS (
                SELECT id, sum(1.0 / (:rrf_k + rnk)) AS rrf
                FROM (SELECT id, rnk FROM dense UNION ALL SELECT id, rnk FROM lexical) ranked
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
            "word_query": word_query,
            "qvec": _vector_literal(query_embedding),
            "pool": CANDIDATE_POOL,
            "rrf_k": RRF_K,
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
) -> list[RetrievedChunk]:
    if mode == "hybrid":
        return await hybrid_search(db, question, query_embedding, top_k)
    return await similarity_search(db, query_embedding, top_k)

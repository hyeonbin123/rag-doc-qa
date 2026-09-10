import uuid
from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

SCORE_FLOOR = 0.3


@dataclass
class RetrievedChunk:
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    source_path: str
    heading_path: str | None
    content: str
    score: float


async def similarity_search(
    db: AsyncSession, query_embedding: list[float], top_k: int
) -> list[RetrievedChunk]:
    """Cosine similarity search over chunks via pgvector's <=> operator.

    `1 - (embedding <=> :qvec)` converts cosine *distance* into a
    similarity score in roughly [0, 1] for normalized vectors.
    """
    vector_literal = "[" + ",".join(str(x) for x in query_embedding) + "]"
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
        {"qvec": vector_literal, "top_k": top_k},
    )

    chunks = [
        RetrievedChunk(
            chunk_id=row.id,
            document_id=row.document_id,
            source_path=row.source_path,
            heading_path=row.heading_path,
            content=row.content,
            score=float(row.score),
        )
        for row in result
    ]
    return [c for c in chunks if c.score >= SCORE_FLOOR]

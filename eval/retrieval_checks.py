"""Checks the eval scripts run against the database before measuring.

The embedding comparison (docs/experiments.md v12) points the same scripts at several
databases, each embedded by a different model, and picks the model by environment
variable. Measuring one model's questions against another model's vectors would not
fail; it would just give wrong numbers. check_stored_vectors catches that.
"""

from __future__ import annotations

import json
import math

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.chunking import build_embedding_text
from app.services.embedding import EmbeddingService
from app.services.retrieval import dense_search_sql

MIN_COSINE = 0.99


class VectorModelMismatch(RuntimeError):
    """The stored vectors of a language were not made by the model the run would use."""


async def force_exact_search(db: AsyncSession) -> None:
    """Make this session's vector searches exact scans instead of HNSW index scans.

    With index scans off the planner sorts every row of the language by distance, which
    is the exact top-k the approximate HNSW scan is compared against.
    """
    await db.execute(text("SET enable_indexscan = off"))


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))


async def check_stored_vectors(
    db: AsyncSession, embedder: EmbeddingService, language: str, sample: int = 3
) -> dict:
    """Re-embed a few stored chunks of `language` and compare with their stored vectors.

    Ingestion embeds build_embedding_text(heading_path, content), so the same model gives
    back the stored vector (cosine about 1.0); another model's vectors are unrelated.
    """
    rows = (
        await db.execute(
            text(
                "SELECT heading_path, content, embedding::text AS embedding FROM chunks "
                "WHERE language = :language ORDER BY id LIMIT :n"
            ),
            {"language": language, "n": sample},
        )
    ).all()
    if not rows:
        raise VectorModelMismatch(f"no {language} chunks in this database")
    fresh = embedder.embed_passages([build_embedding_text(r.heading_path or "", r.content) for r in rows])
    cosines = [_cosine(json.loads(r.embedding), v) for r, v in zip(rows, fresh, strict=True)]
    result = {
        "language": language,
        "model": embedder.identity,
        "checked": len(rows),
        "min_cosine": round(min(cosines), 6),
    }
    if result["min_cosine"] < MIN_COSINE:
        raise VectorModelMismatch(
            f"stored {language} vectors were not made by {embedder.identity} "
            f"(cosine {result['min_cosine']} < {MIN_COSINE}); wrong DATABASE_URL or model?"
        )
    return result


async def dense_search_plan(db: AsyncSession, language: str, top_k: int = 10) -> list[str]:
    """The scan nodes Postgres picks for the dense search of `language`.

    "Index Scan using chunks_embedding_<language>_hnsw_idx" is the approximate HNSW scan;
    "Seq Scan on chunks" under a Sort is an exact scan. With a few hundred chunks per
    language the planner can prefer the exact one. One stored vector stands in for a query.
    """
    vector = (
        await db.execute(
            text("SELECT embedding::text FROM chunks WHERE language = :language ORDER BY id LIMIT 1"),
            {"language": language},
        )
    ).scalar()
    if vector is None:
        return []
    plan = await db.execute(
        text("EXPLAIN " + dense_search_sql(language)), {"qvec": vector, "top_k": top_k}
    )
    nodes = [line.split("(cost")[0].replace("->", "").strip() for (line,) in plan if "(cost" in line]
    return [node for node in nodes if "Scan" in node or node == "Sort"]

"""Retrieval-only evaluation: Hit@k and MRR against eval/qa_dataset.jsonl.

Usage:
    python -m eval.run_retrieval_eval [--top-k 10] [--tag v1_baseline] [--mode dense|hybrid]
"""

from __future__ import annotations

import argparse
import asyncio
from datetime import UTC, datetime

from app.config import get_settings
from app.db.session import async_session_maker
from app.services.embedding import get_embedding_service
from app.services.retrieval import RetrievalMode, retrieve
from eval.common import EvalQuestion, load_dataset, write_report


def hit_at_k(ranked_paths: list[str], expected: list[str], k: int) -> bool:
    return any(p in expected for p in ranked_paths[:k])


def reciprocal_rank(ranked_paths: list[str], expected: list[str]) -> float:
    for rank, path in enumerate(ranked_paths, start=1):
        if path in expected:
            return 1.0 / rank
    return 0.0


async def evaluate_question(db, embedder, q: EvalQuestion, top_k: int, mode: RetrievalMode) -> dict:
    query_vector = embedder.embed_query(q.question)
    retrieved = await retrieve(db, q.question, query_vector, top_k, mode)
    ranked_paths = [r.source_path for r in retrieved]

    return {
        "id": q.id,
        "question": q.question,
        "hit@3": hit_at_k(ranked_paths, q.expected_source_paths, 3),
        "hit@5": hit_at_k(ranked_paths, q.expected_source_paths, 5),
        "hit@10": hit_at_k(ranked_paths, q.expected_source_paths, 10),
        "reciprocal_rank": reciprocal_rank(ranked_paths, q.expected_source_paths),
        "retrieved_paths": ranked_paths,
    }


async def main(top_k: int, tag: str, mode: RetrievalMode | None) -> None:
    settings = get_settings()
    mode = mode or settings.retrieval_mode
    embedder = get_embedding_service()
    questions = load_dataset()

    results = []
    async with async_session_maker() as db:
        for q in questions:
            results.append(await evaluate_question(db, embedder, q, top_k, mode))

    n = len(results)
    agg = {
        "hit@3": sum(r["hit@3"] for r in results) / n,
        "hit@5": sum(r["hit@5"] for r in results) / n,
        "hit@10": sum(r["hit@10"] for r in results) / n,
        "mrr": sum(r["reciprocal_rank"] for r in results) / n,
    }

    lines = [
        f"# Retrieval eval report ({tag})",
        "",
        f"- date: {datetime.now(UTC).isoformat()}",
        f"- embedding model: {settings.embedding_model_name}",
        f"- top_k: {top_k}",
        f"- retrieval mode: {mode}",
        f"- questions: {n}",
        "",
        "## Aggregate metrics",
        "",
        "| Hit@3 | Hit@5 | Hit@10 | MRR |",
        "|---|---|---|---|",
        f"| {agg['hit@3']:.2f} | {agg['hit@5']:.2f} | {agg['hit@10']:.2f} | {agg['mrr']:.3f} |",
        "",
        "## Per-question",
        "",
        "| id | hit@3 | hit@5 | hit@10 | RR | question |",
        "|---|---|---|---|---|---|",
    ]
    for r in results:
        lines.append(
            f"| {r['id']} | {r['hit@3']} | {r['hit@5']} | {r['hit@10']} "
            f"| {r['reciprocal_rank']:.2f} | {r['question']} |"
        )

    report = "\n".join(lines)
    print(report)

    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    path = write_report(f"retrieval_eval_{tag}_{timestamp}.md", report)
    print(f"\nwritten to {path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--tag", default="run")
    parser.add_argument("--mode", choices=["dense", "hybrid"], default=None)
    args = parser.parse_args()
    asyncio.run(main(args.top_k, args.tag, args.mode))

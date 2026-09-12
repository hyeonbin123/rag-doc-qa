"""Retrieval-only evaluation: Hit@k, MRR and retrieval latency.

Usage:
    python -m eval.run_retrieval_eval [--top-k 10] [--tag v1_baseline]
        [--mode dense|hybrid|rerank] [--dataset eval/qa_dev.jsonl]
        [--lexical-weight 0.75] [--rerank-pool 10] [--reranker-model NAME]

Tune on the tuning sets (eval/qa_dev.jsonl, eval/qa_dev_ko.jsonl); the other sets are
held out for testing. In rerank mode the model and pool follow each question's
language; --reranker-model and --rerank-pool override them for every question.
"""

from __future__ import annotations

import argparse
import asyncio
import statistics
import time
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

from app.config import get_settings
from app.db.session import async_session_maker
from app.services.embedding import get_embedding_service
from app.services.language import Language, detect_language
from app.services.reranking import RerankerService, get_reranker_service
from app.services.retrieval import LEXICAL_WEIGHT, RERANK_POOLS, retrieve
from eval.common import DATASET_PATH, EvalQuestion, load_dataset, write_report


def hit_at_k(ranked_paths: list[str], expected: list[str], k: int) -> bool:
    return any(p in expected for p in ranked_paths[:k])


def reciprocal_rank(ranked_paths: list[str], expected: list[str]) -> float:
    for rank, path in enumerate(ranked_paths, start=1):
        if path in expected:
            return 1.0 / rank
    return 0.0


def reranker_lookup(model_override: str | None) -> Callable[[Language], RerankerService]:
    if model_override is None:
        return get_reranker_service  # the configured model for each question's language
    fixed = RerankerService(model_override)
    return lambda language: fixed


async def evaluate_question(
    db,
    embedder,
    q: EvalQuestion,
    args: argparse.Namespace,
    reranker_for: Callable[[Language], RerankerService] | None,
) -> dict:
    language = detect_language(q.question)
    query_vector = embedder(language).embed_query(q.question)
    reranker = reranker_for(language) if reranker_for else None
    # Timed after the embedding so every mode is measured on the same work: the DB
    # queries, plus the cross-encoder in rerank mode.
    start = time.perf_counter()
    retrieved = await retrieve(
        db,
        q.question,
        query_vector,
        args.top_k,
        args.mode,
        language=language,
        lexical_weight=args.lexical_weight,
        reranker=reranker,
        rerank_pool=args.rerank_pool,
    )
    latency_ms = (time.perf_counter() - start) * 1000
    ranked_paths = [r.source_path for r in retrieved]

    return {
        "id": q.id,
        "question": q.question,
        "hit@3": hit_at_k(ranked_paths, q.expected_source_paths, 3),
        "hit@5": hit_at_k(ranked_paths, q.expected_source_paths, 5),
        "hit@10": hit_at_k(ranked_paths, q.expected_source_paths, 10),
        "reciprocal_rank": reciprocal_rank(ranked_paths, q.expected_source_paths),
        "retrieved_paths": ranked_paths,
        "latency_ms": latency_ms,
    }


async def main(args: argparse.Namespace) -> None:
    settings = get_settings()
    args.mode = args.mode or settings.retrieval_mode
    embedder = get_embedding_service  # per-language lookup, called with each question's language
    questions = load_dataset(args.dataset)
    languages = sorted({detect_language(q.question) for q in questions})

    reranker_for = None
    if args.mode == "rerank":
        reranker_for = reranker_lookup(args.reranker_model)
        for language in languages:  # keep one-off setup cost out of the timings
            reranker_for(language).score("warm-up", ["warm-up"])

    results = []
    async with async_session_maker() as db:
        for q in questions:
            results.append(await evaluate_question(db, embedder, q, args, reranker_for))

    n = len(results)
    latencies = [r["latency_ms"] for r in results]
    agg = {
        "hit@3": sum(r["hit@3"] for r in results) / n,
        "hit@5": sum(r["hit@5"] for r in results) / n,
        "hit@10": sum(r["hit@10"] for r in results) / n,
        "mrr": sum(r["reciprocal_rank"] for r in results) / n,
        "p50": statistics.median(latencies),
        "p95": statistics.quantiles(latencies, n=20)[18],
    }

    lines = [
        f"# Retrieval eval report ({args.tag})",
        "",
        f"- date: {datetime.now(UTC).isoformat()}",
        f"- embedding models: en {settings.embedding_model_name}, ko {settings.embedding_model_name_ko}",
        f"- database: {settings.database_url.rsplit('/', 1)[-1]}",
        f"- top_k: {args.top_k}",
        f"- retrieval mode: {args.mode}",
    ]
    if args.mode == "hybrid":
        lines.append(f"- lexical: BM25, RRF weight {args.lexical_weight}")
    if args.mode == "rerank":
        for language in languages:
            model = args.reranker_model or settings.reranker_model_for(language)
            pool = args.rerank_pool or RERANK_POOLS[language]
            lines.append(f"- reranker ({language}): {model}, top {pool} of each of dense and BM25")
    lines += [
        f"- dataset: {args.dataset.name}",
        f"- questions: {n}",
        "- latency: retrieval only (after the query embedding), this machine's CPU",
        "",
        "## Aggregate metrics",
        "",
        "| Hit@3 | Hit@5 | Hit@10 | MRR | latency p50 (ms) | latency p95 (ms) |",
        "|---|---|---|---|---|---|",
        f"| {agg['hit@3']:.2f} | {agg['hit@5']:.2f} | {agg['hit@10']:.2f} | {agg['mrr']:.3f} "
        f"| {agg['p50']:.0f} | {agg['p95']:.0f} |",
        "",
        "## Per-question",
        "",
        "| id | hit@3 | hit@5 | hit@10 | RR | ms | question |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in results:
        lines.append(
            f"| {r['id']} | {r['hit@3']} | {r['hit@5']} | {r['hit@10']} "
            f"| {r['reciprocal_rank']:.2f} | {r['latency_ms']:.0f} | {r['question']} |"
        )

    report = "\n".join(lines)
    print(report)

    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    path = write_report(f"retrieval_eval_{args.tag}_{timestamp}.md", report)
    print(f"\nwritten to {path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--tag", default="run")
    parser.add_argument("--mode", choices=["dense", "hybrid", "rerank"], default=None)
    parser.add_argument("--dataset", type=Path, default=DATASET_PATH)
    parser.add_argument("--lexical-weight", type=float, default=LEXICAL_WEIGHT)
    parser.add_argument(
        "--rerank-pool", type=int, default=None, help="defaults to RERANK_POOLS[language]"
    )
    parser.add_argument(
        "--reranker-model", default=None, help="defaults to the language's RERANKER_MODEL_NAME"
    )
    asyncio.run(main(parser.parse_args()))

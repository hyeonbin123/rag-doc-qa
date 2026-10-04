"""Retrieval-only evaluation: Hit@k, MRR and retrieval latency.

Usage:
    python -m eval.run_retrieval_eval [--top-k 10] [--tag v1_baseline]
        [--mode dense|hybrid|rerank] [--dataset eval/qa_dev.jsonl [more.jsonl ...]]
        [--lexical-weight 0.75] [--rerank-pool 10] [--reranker-model NAME]
        [--score-floor 0.3] [--cross-lingual] [--exact] [--no-vector-check]

Tune on the tuning sets (eval/qa_dev.jsonl, eval/qa_dev_ko.jsonl, eval/qa_dev2_ko.jsonl);
the other sets are held out for testing. In rerank mode the model and pool follow each
question's language; --reranker-model and --rerank-pool override them for every question.

A hit is a retrieved chunk from an expected page in any translation, so an English chunk
of an expected Korean page counts (the --cross-lingual search can return one). For a
one-language search this is the same as matching the path exactly.

Every run also writes per-question records (ranked chunk ids, paths and scores) to
eval/runs/<tag>.retrieval.jsonl; eval/retrieval_runs.py compares runs and score floors.
"""

from __future__ import annotations

import argparse
import asyncio
import statistics
import time
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

import torch

from app.config import get_settings
from app.db.session import async_session_maker
from app.services.embedding import get_embedding_service
from app.services.language import Language, detect_language
from app.services.reranking import RerankerService, get_reranker_service
from app.services.retrieval import LEXICAL_WEIGHT, RERANK_POOLS, page_key, retrieve, score_floor_for
from eval.common import (
    DATASET_PATH,
    RUNS_DIR,
    EvalQuestion,
    git_commit,
    load_dataset,
    write_json,
    write_jsonl,
    write_report,
)
from eval.retrieval_checks import check_stored_vectors, dense_search_plan, force_exact_search

SHORT = 5  # fewer results than this means the generator would get fewer than top 5


def _pages(paths: list[str]) -> list[str]:
    return [page_key(p) for p in paths]


def hit_at_k(ranked_paths: list[str], expected: list[str], k: int) -> bool:
    expected_pages = set(_pages(expected))
    return any(p in expected_pages for p in _pages(ranked_paths[:k]))


def reciprocal_rank(ranked_paths: list[str], expected: list[str]) -> float:
    expected_pages = set(_pages(expected))
    for rank, page in enumerate(_pages(ranked_paths), start=1):
        if page in expected_pages:
            return 1.0 / rank
    return 0.0


def reranker_lookup(model_override: str | None) -> Callable[[Language], RerankerService]:
    if model_override is None:
        return get_reranker_service  # the configured model for each question's language
    fixed = RerankerService(model_override)
    return lambda language: fixed


def question_floor(args: argparse.Namespace, embedder, language: Language) -> float:
    """--score-floor if given, else the floor of the model that embeds this language."""
    if args.score_floor is not None:
        return args.score_floor
    return score_floor_for(embedder(language).model_name)


async def evaluate_question(
    db,
    embedder,
    q: EvalQuestion,
    args: argparse.Namespace,
    reranker_for: Callable[[Language], RerankerService] | None,
    dataset: str = "",
) -> dict:
    language = detect_language(q.question)
    query_vector = embedder(language).embed_query(q.question)
    reranker = reranker_for(language) if reranker_for else None
    floor = question_floor(args, embedder, language)
    cross_lingual = bool(args.cross_lingual) and language == "ko"
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
        score_floor=floor,
        cross_lingual=cross_lingual,
    )
    latency_ms = (time.perf_counter() - start) * 1000
    ranked_paths = [r.source_path for r in retrieved]

    return {
        "id": q.id,
        "dataset": dataset,
        "question": q.question,
        "language": language,
        "expected_source_paths": q.expected_source_paths,
        "cross_lingual": cross_lingual,
        "score_floor": floor,
        "results": [
            {
                "rank": rank,
                "chunk_id": str(r.chunk_id),
                "source_path": r.source_path,
                "score": round(float(r.score), 6),
            }
            for rank, r in enumerate(retrieved, start=1)
        ],
        "n_results": len(retrieved),
        "hit@3": hit_at_k(ranked_paths, q.expected_source_paths, 3),
        "hit@5": hit_at_k(ranked_paths, q.expected_source_paths, 5),
        "hit@10": hit_at_k(ranked_paths, q.expected_source_paths, 10),
        "reciprocal_rank": reciprocal_rank(ranked_paths, q.expected_source_paths),
        "retrieved_paths": ranked_paths,
        "latency_ms": latency_ms,
    }


def aggregate(results: list[dict]) -> dict:
    n = len(results)
    latencies = [r["latency_ms"] for r in results]
    return {
        "n": n,
        "hit@3": sum(r["hit@3"] for r in results) / n,
        "hit@5": sum(r["hit@5"] for r in results) / n,
        "hit@10": sum(r["hit@10"] for r in results) / n,
        "mrr": sum(r["reciprocal_rank"] for r in results) / n,
        "short": sum(r["n_results"] < SHORT for r in results),
        "p50": statistics.median(latencies),
        "p95": statistics.quantiles(latencies, n=20)[18] if n > 1 else latencies[0],
    }


def _aggregate_row(label: str, agg: dict) -> str:
    return (
        f"| {label} | {agg['n']} | {agg['hit@3']:.2f} | {agg['hit@5']:.2f} | {agg['hit@10']:.2f} "
        f"| {agg['mrr']:.3f} | {agg['short']} | {agg['p50']:.0f} | {agg['p95']:.0f} |"
    )


async def main(args: argparse.Namespace) -> None:
    settings = get_settings()
    args.mode = args.mode or settings.retrieval_mode
    if args.cross_lingual and args.mode != "dense":
        raise SystemExit("--cross-lingual is dense only")
    embedder = get_embedding_service  # per-language lookup, called with each question's language
    datasets = [(path, load_dataset(path)) for path in args.dataset]
    languages = sorted({detect_language(q.question) for _, qs in datasets for q in qs})

    reranker_for = None
    if args.mode == "rerank":
        reranker_for = reranker_lookup(args.reranker_model)
        for language in languages:  # keep one-off setup cost out of the timings
            reranker_for(language).score("warm-up", ["warm-up"])

    started = datetime.now(UTC)
    results = []
    vector_checks = []
    async with async_session_maker() as db:
        if not args.no_vector_check:
            # The stored vectors of every searched language must come from the model that
            # embeds the questions searching them (a cross-lingual Korean question searches
            # the English chunks with the Korean model).
            for language in languages:
                vector_checks.append(await check_stored_vectors(db, embedder(language), language))
            if args.cross_lingual and "ko" in languages:
                vector_checks.append(await check_stored_vectors(db, embedder("ko"), "en"))
        if args.exact:
            await force_exact_search(db)
        searched = set(languages) | ({"en"} if args.cross_lingual and "ko" in languages else set())
        plans = {lang: await dense_search_plan(db, lang, args.top_k) for lang in sorted(searched)}
        for path, questions in datasets:
            for q in questions:
                results.append(await evaluate_question(db, embedder, q, args, reranker_for, path.name))

    agg = aggregate(results)
    floors = {lang: question_floor(args, embedder, lang) for lang in languages}
    lines = [
        f"# Retrieval eval report ({args.tag})",
        "",
        f"- date: {started.isoformat()}",
        f"- embedding models: en {settings.embedding_model_name}, ko {settings.embedding_model_name_ko}",
        f"- database: {settings.database_url.rsplit('/', 1)[-1]}",
        f"- top_k: {args.top_k}",
        f"- retrieval mode: {args.mode}"
        + (" (Korean questions search the Korean and English chunks, one translation per page)"
           if args.cross_lingual else ""),
        f"- search: {'exact (index scans off)' if args.exact else 'as planned'}; dense plan: "
        + "; ".join(f"{lang} {' > '.join(nodes)}" for lang, nodes in plans.items()),
        f"- score floor: {', '.join(f'{lang} {floor}' for lang, floor in floors.items())}"
        + (" (dense only)" if args.mode != "dense" else ""),
    ]
    if vector_checks:
        lines.append(
            "- stored vectors checked: "
            + ", ".join(
                f"{c['language']} chunks vs {c['model']} (min cosine {c['min_cosine']})"
                for c in vector_checks
            )
        )
    if args.mode == "hybrid":
        lines.append(f"- lexical: BM25, RRF weight {args.lexical_weight}")
    if args.mode == "rerank":
        for language in languages:
            model = args.reranker_model or settings.reranker_model_for(language)
            pool = args.rerank_pool or RERANK_POOLS[language]
            lines.append(f"- reranker ({language}): {model}, top {pool} of each of dense and BM25")
    lines += [
        f"- dataset: {', '.join(path.name for path, _ in datasets)}",
        f"- questions: {agg['n']}",
        "- hit: a chunk of an expected page, in any translation",
        f"- short: questions with fewer than {SHORT} results (the score floor cut the rest)",
        "- latency: retrieval only (after the query embedding), this machine's CPU",
        "",
        "## Aggregate metrics",
        "",
        "| set | questions | Hit@3 | Hit@5 | Hit@10 | MRR | short | latency p50 (ms) | latency p95 (ms) |",
        "|---|---|---|---|---|---|---|---|---|",
        _aggregate_row("all", agg),
    ]
    if len(datasets) > 1:
        for path, _ in datasets:
            subset = [r for r in results if r["dataset"] == path.name]
            lines.append(_aggregate_row(path.name, aggregate(subset)))
    lines += [
        "",
        "## Per-question",
        "",
        "| id | hit@3 | hit@5 | hit@10 | RR | results | ms | question |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in results:
        lines.append(
            f"| {r['id']} | {r['hit@3']} | {r['hit@5']} | {r['hit@10']} "
            f"| {r['reciprocal_rank']:.2f} | {r['n_results']} | {r['latency_ms']:.0f} | {r['question']} |"
        )

    report = "\n".join(lines)
    print(report)

    records_path = write_jsonl(
        RUNS_DIR / f"{args.tag}.retrieval.jsonl",
        [{k: v for k, v in r.items() if k != "retrieved_paths"} for r in results],
    )
    write_json(
        RUNS_DIR / f"{args.tag}.retrieval.meta.json",
        {
            "date": started.isoformat(),
            "tag": args.tag,
            "git_commit": git_commit(),
            "database": settings.database_url.rsplit("/", 1)[-1],
            "embedding_models": {lang: embedder(lang).identity for lang in languages},
            "mode": args.mode,
            "top_k": args.top_k,
            "score_floors": floors,
            "cross_lingual": bool(args.cross_lingual),
            "exact": bool(args.exact),
            "dense_plans": plans,
            "datasets": [path.name for path, _ in datasets],
            "vector_checks": vector_checks,
            "torch_threads": torch.get_num_threads(),
            "aggregate": agg,
        },
    )
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    path = write_report(f"retrieval_eval_{args.tag}_{timestamp}.md", report)
    print(f"\nwritten to {path} and {records_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--tag", default="run")
    parser.add_argument("--mode", choices=["dense", "hybrid", "rerank"], default=None)
    parser.add_argument("--dataset", type=Path, nargs="+", default=[DATASET_PATH])
    parser.add_argument("--lexical-weight", type=float, default=LEXICAL_WEIGHT)
    parser.add_argument(
        "--rerank-pool", type=int, default=None, help="defaults to RERANK_POOLS[language]"
    )
    parser.add_argument(
        "--reranker-model", default=None, help="defaults to the language's RERANKER_MODEL_NAME"
    )
    parser.add_argument(
        "--score-floor", type=float, default=None,
        help="dense score floor for every question; defaults to each model's (SCORE_FLOORS)",
    )
    parser.add_argument(
        "--cross-lingual", action="store_true",
        help="Korean questions search the Korean and English chunks (needs a database whose "
        "English chunks were embedded by the Korean model)",
    )
    parser.add_argument("--exact", action="store_true", help="exact search instead of HNSW")
    parser.add_argument(
        "--no-vector-check", action="store_true",
        help="skip checking that the stored vectors come from the configured models",
    )
    asyncio.run(main(parser.parse_args()))

"""CPU query-embedding latency of an embedding model: the v12 budget gate G1.

Usage:
    python -m eval.embedding_latency MODEL --dataset eval/qa_dev_ko.jsonl eval/qa_dev2_ko.jsonl
        [--passes 3] [--tag v12_latency_<name>]

Loads the model the way the app does (EmbeddingService: its prefixes, revision, cut and
float32), embeds three warm-up questions, then embeds every question one call at a time
through embed_query, `passes` times over, and reports the per-call p50/p95/mean. Only the
question texts are used: no labels, no retrieval.

Also checks that embedding a batch gives the same vectors as one-at-a-time calls (padding
and pooling handled right) and, for last-token pooling, that the tokenized input ends with
the end-of-text token.
"""

from __future__ import annotations

import argparse
import math
import platform
import statistics
import time
from datetime import UTC, datetime
from pathlib import Path

import torch

from app.services.embedding import EmbeddingService
from eval.common import RUNS_DIR, load_dataset, write_json, write_report


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))


def measure(model_name: str, questions: list[str], passes: int) -> dict:
    start = time.perf_counter()
    service = EmbeddingService(model_name)
    load_s = time.perf_counter() - start
    for q in questions[:3]:
        service.embed_query(q)

    timings_ms = []
    for _ in range(passes):
        for q in questions:
            t = time.perf_counter()
            service.embed_query(q)
            timings_ms.append((time.perf_counter() - t) * 1000)

    sample = questions[:8]
    single = [service.embed_passages([q])[0] for q in sample]
    batch = service.embed_passages(sample)
    consistency = min(_cosine(a, b) for a, b in zip(single, batch, strict=True))

    model = service._model
    pooling = getattr(model[1], "pooling_mode", None) if len(model) > 1 else None
    ends_with_eos = None
    if pooling == "lasttoken":
        ids = model.tokenizer("경로 매개변수")["input_ids"]
        ends_with_eos = ids[-1] == model.tokenizer.eos_token_id

    return {
        "model": service.identity,
        "load_s": round(load_s, 1),
        "calls": len(timings_ms),
        "p50_ms": round(statistics.median(timings_ms), 1),
        "p95_ms": round(statistics.quantiles(timings_ms, n=20)[18], 1),
        "mean_ms": round(statistics.fmean(timings_ms), 1),
        "max_ms": round(max(timings_ms), 1),
        "batch_vs_single_min_cosine": round(consistency, 6),
        "pooling": pooling,
        "last_token_is_eos": ends_with_eos,
        "dtype": str(next(model.parameters()).dtype),
        "max_seq_length": model.max_seq_length,
    }


def main(args: argparse.Namespace) -> None:
    questions = [q.question for path in args.dataset for q in load_dataset(path)]
    started = datetime.now(UTC).isoformat()
    result = measure(args.model, questions, args.passes)
    result.update(
        date=started,
        tag=args.tag,
        datasets=[p.name for p in args.dataset],
        questions=len(questions),
        passes=args.passes,
        torch_threads=torch.get_num_threads(),
        cpu=platform.processor(),
    )
    lines = [
        f"# Query embedding latency ({args.tag})",
        "",
        f"- date: {started}",
        f"- model: {result['model']} ({result['dtype']}, pooling {result['pooling']})",
        f"- CPU: {result['cpu']}, torch threads {result['torch_threads']}",
        f"- questions: {len(questions)} from {', '.join(result['datasets'])}, {args.passes} passes, "
        "one embed_query call each, after 3 warm-up calls",
        "",
        "| p50 (ms) | p95 (ms) | mean (ms) | max (ms) | load (s) | batch vs single min cosine "
        "| last token is EOS |",
        "|---|---|---|---|---|---|---|",
        f"| {result['p50_ms']} | {result['p95_ms']} | {result['mean_ms']} | {result['max_ms']} "
        f"| {result['load_s']} | {result['batch_vs_single_min_cosine']} | {result['last_token_is_eos']} |",
    ]
    report = "\n".join(lines)
    print(report)
    write_json(RUNS_DIR / f"{args.tag}.latency.json", result)
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    print(f"\nwritten to {write_report(f'embedding_latency_{args.tag}_{timestamp}.md', report)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("model")
    parser.add_argument("--dataset", type=Path, nargs="+", required=True)
    parser.add_argument("--passes", type=int, default=3)
    parser.add_argument("--tag", default="latency")
    main(parser.parse_args())

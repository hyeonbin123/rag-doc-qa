"""Markdown report for an answer-eval run: aggregates and a per-question table.

Used by eval/run_answer_eval.py (generate + judge) and eval/run_judge.py (judge stored
answers). The per-item JSONL files the report names hold everything shown here.
"""

from __future__ import annotations

import statistics
from datetime import UTC, datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def display_path(path: Path | str | None) -> str:
    if path is None:
        return "-"
    path = Path(path).resolve()
    try:
        return path.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _avg(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def _fmt(value: float | None, spec: str = ".2f") -> str:
    return "n/a" if value is None else format(value, spec)


def summarize(records: list[dict], judgments: list[dict] | None) -> dict:
    by_id = {j["id"]: j for j in judgments or []}
    scored = [by_id[r["id"]] for r in records if by_id.get(r["id"], {}).get("correctness_score") is not None]
    return {
        "n": len(records),
        "coverage": _avg([r["keyword_coverage"] for r in records]),
        "faithfulness": _avg([j["faithfulness_score"] for j in scored]),
        "correctness": _avg([j["correctness_score"] for j in scored]),
        "correctness_sum": sum(j["correctness_score"] for j in scored) if scored else None,
        "scored": len(scored),
        "hallucinated": sum(1 for j in scored if j["hallucinated"]),
        "generation_p50": statistics.median(r["generation_ms"] for r in records),
        "kana_han": sum(1 for r in records if r["kana_han"]),
        "truncated": sum(1 for j in by_id.values() if j["truncation"] == "truncated"),
        "unchecked": sum(1 for j in by_id.values() if j["truncation"] == "unchecked" and j["raw"]),
        "errors": sum(1 for j in by_id.values() if j["error"]),
    }


def generation_notes(gen_meta: dict, records: list[dict]) -> list[str]:
    """v13 run notes: the model digest, think and guard settings, per-call stop reasons."""
    n = len(records)
    calls = [r.get("generation_calls") for r in records]
    lines = []
    if gen_meta.get("model_digest"):
        lines.append(f"- model digest: {gen_meta['model_digest']}")
    if "think" in gen_meta or "language_guard" in gen_meta:
        guard = "on" if gen_meta.get("language_guard") else "off"
        if gen_meta.get("language_guard"):
            guard += f" (regenerated {sum(1 for r in records if r.get('guard_applied'))}/{n})"
        lines.append(f"- think: {gen_meta.get('think')}, language guard: {guard}")
    if any(calls):
        cut = sum(1 for c in calls if c and c["answer"][-1].get("done_reason") == "length")
        thinking = sum(
            1
            for r, c in zip(records, calls, strict=True)
            if c
            and (
                r.get("think_tag_in_answer")
                or any(x.get("thinking_chars") for x in [*c["answer"], c["citation"]])
            )
        )
        bad = sum(1 for r in records if r.get("citation_schema_error"))
        lines.append(
            f"- final answer call stopped by the output limit, done_reason=length: {cut}/{n}; "
            f"reasoning output: {thinking}/{n}; citation replies breaking the schema: {bad}/{n}"
        )
    return lines


def judge_description(judge_meta: dict | None) -> list[str]:
    if judge_meta is None:
        return ["- judge: skipped"]
    num_ctx = judge_meta["num_ctx"]
    context = "Ollama default (num_ctx not sent, truncation on)" if num_ctx is None else (
        f"num_ctx {num_ctx}, truncate=false"
    )
    counter = judge_meta.get("tokenizer") or "none (truncation unchecked)"
    return [
        f"- judge: {judge_meta['label']}, {judge_meta['model']}, {context}",
        "- judge context in use (Ollama /api/ps after judging): "
        f"{judge_meta.get('context_in_use') or 'unknown'}",
        f"- judge prompt token counter: {counter}",
        f"- judge order: {judge_meta.get('order', 'dataset')}",
        f"- judge date: {judge_meta.get('date', '-')}",
    ]


def render_report(
    tag: str,
    gen_meta: dict,
    records: list[dict],
    judgments: list[dict] | None,
    judge_meta: dict | None,
) -> str:
    s = summarize(records, judgments)
    by_id = {j["id"]: j for j in judgments or []}
    order = gen_meta.get("order", "dataset")
    if order == "shuffle":
        order = f"shuffle (seed {gen_meta.get('seed')})"
    lines = [
        f"# Answer eval report ({tag})",
        "",
        f"- date: {datetime.now(UTC).isoformat()}",
        f"- generated: {gen_meta.get('date', '-')}",
        f"- provider: {gen_meta.get('provider', '-')}",
        f"- model: {gen_meta.get('model', '-')}",
        *generation_notes(gen_meta, records),
        *judge_description(judge_meta),
        f"- ollama version: {gen_meta.get('ollama_version') or '-'} (generation)"
        + (f", {judge_meta.get('ollama_version') or '-'} (judge)" if judge_meta else ""),
        f"- top_k: {gen_meta.get('top_k', '-')}",
        f"- retrieval mode: {gen_meta.get('retrieval_mode', '-')}"
        + (
            " (Korean questions search the Korean and English chunks)"
            if gen_meta.get("cross_lingual")
            else ""
        ),
        f"- database: {gen_meta.get('database', '-')}, "
        f"embedding models: {gen_meta.get('embedding_models', '-')}",
        f"- dataset: {gen_meta.get('dataset', '-')}",
        f"- questions: {s['n']}",
        f"- generation order: {order}",
        "- generation time: both generation calls (answer + citations), this machine's GPU",
        f"- per-item records: {display_path(gen_meta.get('records_path'))}"
        + (f", {display_path(judge_meta.get('judgments_path'))}" if judge_meta else ""),
        "",
        "## Aggregate metrics",
        "",
        "| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum "
        "| Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated "
        "| Judge errors |",
        "|---|---|---|---|---|---|---|---|---|",
        f"| {_fmt(s['coverage'])} | {_fmt(s['faithfulness'])} | {_fmt(s['correctness'])} "
        f"| {_fmt(s['correctness_sum'], 'd')} | {s['hallucinated']}/{s['scored']} "
        f"| {s['generation_p50']:.0f} | {s['kana_han']}/{s['n']} "
        f"| {s['truncated']}/{s['scored'] + s['errors']}"
        + (f" ({s['unchecked']} unchecked)" if s["unchecked"] else "")
        + f" | {s['errors']} |",
        "",
        "## Per-question",
        "",
        "| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han "
        "| judge prompt tokens (counted / read) | truncation |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for r in records:
        j = by_id.get(r["id"], {})
        lines.append(
            f"| {r['id']} | {r['keyword_coverage']:.2f} | {j.get('faithfulness_score')} "
            f"| {j.get('correctness_score')} | {j.get('hallucinated')} | {r['generation_ms']:.0f} "
            f"| {r['kana_han']} | {j.get('prompt_tokens_counted')} / {j.get('prompt_eval_count')} "
            f"| {j.get('truncation', '-')} |"
        )
    lines += ["", "## Worst questions (lowest keyword coverage)", ""]
    for r in sorted(records, key=lambda r: r["keyword_coverage"])[:5]:
        lines.append(f"- **{r['id']}** ({r['keyword_coverage']:.2f}): {r['question']}")
        lines.append(f"  > {r['answer'][:200]}")
    errors = [j for j in by_id.values() if j["error"]]
    if errors:
        lines += ["", "## Judge errors", ""]
        lines += [f"- **{j['id']}**: {j['error']}" for j in errors]
    return "\n".join(lines)

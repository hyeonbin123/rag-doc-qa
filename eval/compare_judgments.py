"""Compare judgment runs item by item, and summarize judge-prompt truncation.

pair: matches two groups of eval/runs/*.judge.jsonl files by dataset and question id.
Per dataset (and pooled) it reports both sums, the mean per-item difference (b - a) with
a paired bootstrap 90% interval, how many items went up / down, and how many stored
answers differ. Used for one judge against another on the same answers (J1 vs J0), and
for two generation passes under one judge (the generation-to-generation noise).

truncation: per file, how many judge prompts came back cut (prompt_eval_count short of
the tokenizer count by more than the tolerance), how many were longer than the context
before sending, and how far Ollama's count and the tokenizer's differ on prompts that
were not cut (the counter's calibration).

Usage:
    python -m eval.compare_judgments pair --title "J1 - J0, pass A" --tag v11_j1_vs_j0_A
        --a eval/runs/v11_A_*.J0.judge.jsonl --b eval/runs/v11_A_*.J1.judge.jsonl
        [--split-by-truncation a]
    python -m eval.compare_judgments truncation --tag v11_truncation_J0 --ctx 4096
        eval/runs/v11_*.J0.judge.jsonl
"""

from __future__ import annotations

import argparse
import random
import statistics
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from eval.answer_report import display_path
from eval.common import read_jsonl, write_report
from eval.judge import TRUNCATION_TOLERANCE

BOOTSTRAP_RESAMPLES = 10_000
BOOTSTRAP_SEED = 20261003
CONFIDENCE = 0.90
METRICS = ("correctness_score", "faithfulness_score", "hallucinated")


def paired_bootstrap_ci(
    diffs: list[float],
    n_resamples: int = BOOTSTRAP_RESAMPLES,
    confidence: float = CONFIDENCE,
    seed: int = BOOTSTRAP_SEED,
) -> tuple[float, float, float]:
    """Mean of the per-item differences and its percentile bootstrap interval."""
    n = len(diffs)
    mean = sum(diffs) / n
    rng = random.Random(seed)
    means = sorted(sum(diffs[rng.randrange(n)] for _ in range(n)) / n for _ in range(n_resamples))
    low = means[int((1 - confidence) / 2 * n_resamples)]
    high = means[int((1 + confidence) / 2 * n_resamples) - 1]
    return mean, low, high


@dataclass
class Paired:
    ids: list[str]
    a: list[float]
    b: list[float]

    @property
    def diffs(self) -> list[float]:
        return [y - x for x, y in zip(self.a, self.b, strict=True)]

    @property
    def up(self) -> int:
        return sum(1 for d in self.diffs if d > 0)

    @property
    def down(self) -> int:
        return sum(1 for d in self.diffs if d < 0)

    @property
    def same(self) -> int:
        return sum(1 for d in self.diffs if d == 0)

    @property
    def sum_a(self) -> float:
        return sum(self.a)

    @property
    def sum_b(self) -> float:
        return sum(self.b)


def _value(row: dict, metric: str) -> float | None:
    value = row.get(metric)
    return None if value is None else int(value)  # booleans count as 0/1


def pair_metric(a_rows: list[dict], b_rows: list[dict], metric: str) -> Paired:
    """Items scored on both sides, in a's order; the two sides must hold the same items."""
    b_by_id = {r["id"]: r for r in b_rows}
    a_ids = [r["id"] for r in a_rows]
    mismatch = set(a_ids) ^ set(b_by_id)
    if mismatch:
        raise ValueError(f"the two runs hold different items: {', '.join(sorted(mismatch))}")
    ids, a_values, b_values = [], [], []
    for row in a_rows:
        x, y = _value(row, metric), _value(b_by_id[row["id"]], metric)
        if x is not None and y is not None:
            ids.append(row["id"])
            a_values.append(x)
            b_values.append(y)
    return Paired(ids, a_values, b_values)


def answers_changed(a_rows: list[dict], b_rows: list[dict]) -> int:
    b_by_id = {r["id"]: r for r in b_rows}
    return sum(1 for r in a_rows if r.get("answer_sha1") != b_by_id[r["id"]].get("answer_sha1"))


def _by_dataset(paths: list[Path]) -> dict[str, list[dict]]:
    groups: dict[str, list[dict]] = defaultdict(list)
    for path in paths:
        for row in read_jsonl(path):
            groups[row.get("dataset") or path.name].append(row)
    for rows in groups.values():
        rows.sort(key=lambda r: r.get("dataset_index") or 0)
    return dict(groups)


def _ci_cell(paired: Paired) -> str:
    if not paired.ids:
        return "n/a"
    mean, low, high = paired_bootstrap_ci(paired.diffs)
    return f"{mean:+.3f} [{low:+.3f}, {high:+.3f}]"


def _num(value: float) -> str:
    return f"{value:.0f}" if float(value).is_integer() else f"{value:.2f}"


def _pair_row(label: str, a_rows: list[dict], b_rows: list[dict]) -> str:
    cells = [label]
    for metric in METRICS:
        paired = pair_metric(a_rows, b_rows, metric)
        if metric == "correctness_score":
            cells.append(str(len(paired.ids)))
        delta = paired.sum_b - paired.sum_a
        cells.append(f"{_num(paired.sum_a)} -> {_num(paired.sum_b)} ({delta:+.0f})")
        if metric != "hallucinated":
            cells.append(_ci_cell(paired))
            cells.append(f"{paired.up} / {paired.down} / {paired.same}")
    cells.append(str(answers_changed(a_rows, b_rows)))
    return "| " + " | ".join(cells) + " |"


PAIR_HEADER = [
    "| set | n paired | correctness sum a -> b (diff) | correctness mean diff [90% CI] | up / down / same "
    "| faithfulness sum a -> b (diff) | faithfulness mean diff [90% CI] | up / down / same "
    "| hallucinated a -> b (diff) | answers differ |",
    "|---|---|---|---|---|---|---|---|---|---|",
]


def pair_report(
    title: str, a_paths: list[Path], b_paths: list[Path], split_by_truncation: str | None
) -> str:
    a_sets, b_sets = _by_dataset(a_paths), _by_dataset(b_paths)
    if set(a_sets) != set(b_sets):
        raise ValueError(f"datasets differ: a has {sorted(a_sets)}, b has {sorted(b_sets)}")
    lines = [
        f"# Judgment comparison: {title}",
        "",
        f"- date: {datetime.now(UTC).isoformat()}",
        f"- a: {', '.join(display_path(p) for p in a_paths)}",
        f"- b: {', '.join(display_path(p) for p in b_paths)}",
        f"- diff = b - a per item; interval: paired percentile bootstrap, {BOOTSTRAP_RESAMPLES} "
        f"resamples, seed {BOOTSTRAP_SEED}, {CONFIDENCE:.0%}",
        "- items without a score on either side (no passages, judge error) are left out of that metric",
        "",
        *PAIR_HEADER,
    ]
    pooled_a, pooled_b = [], []
    for dataset in sorted(a_sets):
        a_rows, b_rows = a_sets[dataset], b_sets[dataset]
        lines.append(_pair_row(dataset, a_rows, b_rows))
        pooled_a += [{**r, "id": f"{dataset}/{r['id']}"} for r in a_rows]
        pooled_b += [{**r, "id": f"{dataset}/{r['id']}"} for r in b_rows]
    if len(a_sets) > 1:
        lines.append(_pair_row("all sets", pooled_a, pooled_b))

    if split_by_truncation:
        side = pooled_a if split_by_truncation == "a" else pooled_b
        flags = {r["id"]: r.get("truncation") for r in side}
        lines += [
            "",
            f"## Split by the truncation flag of side {split_by_truncation}",
            "",
            *PAIR_HEADER,
        ]
        for flag in ("truncated", "ok"):
            ids = {i for i, f in flags.items() if f == flag}
            if ids:
                lines.append(
                    _pair_row(
                        f"{flag} ({len(ids)})",
                        [r for r in pooled_a if r["id"] in ids],
                        [r for r in pooled_b if r["id"] in ids],
                    )
                )
    return "\n".join(lines)


def truncation_report(paths: list[Path], ctx: int | None) -> str:
    lines = [
        "# Judge prompt truncation",
        "",
        f"- date: {datetime.now(UTC).isoformat()}",
        f"- truncated: prompt_eval_count < tokenizer count - {TRUNCATION_TOLERANCE}",
        "- over context: tokenizer count > context - 1 (Ollama 0.35.1 cuts above that); context = "
        + (f"{ctx} (given)" if ctx else "each run's num_ctx"),
        "- offset: prompt_eval_count - tokenizer count, on prompts that were not cut",
        "",
        "| run | judged | tokens counted p50 / max | over context | truncated | judge errors "
        "| offset median / min / max |",
        "|---|---|---|---|---|---|---|",
    ]
    total = defaultdict(int)
    for path in paths:
        rows = [r for r in read_jsonl(path) if r.get("raw") or r.get("error")]
        context = ctx or (rows[0].get("judge_num_ctx") if rows else None)
        counted = [r["prompt_tokens_counted"] for r in rows if r.get("prompt_tokens_counted") is not None]
        over = sum(1 for n in counted if context and n > context - 1)
        truncated = sum(1 for r in rows if r.get("truncation") == "truncated")
        errors = sum(1 for r in rows if r.get("error"))
        offsets = [
            r["prompt_eval_count"] - r["prompt_tokens_counted"]
            for r in rows
            if r.get("truncation") == "ok"
        ]
        counted_cell = f"{statistics.median(counted):.0f} / {max(counted)}" if counted else "n/a"
        offset_cell = (
            f"{statistics.median(offsets):+.0f} / {min(offsets):+d} / {max(offsets):+d}" if offsets else "n/a"
        )
        lines.append(
            f"| {path.name} | {len(rows)} | {counted_cell} | {over} | {truncated} | {errors} "
            f"| {offset_cell} |"
        )
        total["judged"] += len(rows)
        total["over"] += over
        total["truncated"] += truncated
        total["errors"] += errors
    if len(paths) > 1:
        rate = total["truncated"] / total["judged"] if total["judged"] else 0.0
        lines.append(
            f"| **all** | {total['judged']} | | {total['over']} | {total['truncated']} ({rate:.1%}) "
            f"| {total['errors']} | |"
        )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    pair = sub.add_parser("pair")
    pair.add_argument("--title", required=True)
    pair.add_argument("--tag", required=True)
    pair.add_argument("--a", type=Path, nargs="+", required=True)
    pair.add_argument("--b", type=Path, nargs="+", required=True)
    pair.add_argument("--split-by-truncation", choices=["a", "b"], default=None)
    trunc = sub.add_parser("truncation")
    trunc.add_argument("--tag", required=True)
    trunc.add_argument("--ctx", type=int, default=None, help="context the runs used, if not in the records")
    trunc.add_argument("paths", type=Path, nargs="+")
    args = parser.parse_args()
    sys.stdout.reconfigure(errors="backslashreplace")  # see eval/run_answer_eval.py

    if args.command == "pair":
        report = pair_report(args.title, args.a, args.b, args.split_by_truncation)
        name = f"judge_compare_{args.tag}"
    else:
        report = truncation_report(args.paths, args.ctx)
        name = f"judge_truncation_{args.tag}"
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    path = write_report(f"{name}_{timestamp}.md", report)
    print(report)
    print(f"\nwritten to {path}")


if __name__ == "__main__":
    main()

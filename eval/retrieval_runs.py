"""Analyses of stored retrieval-eval records (eval/runs/<tag>.retrieval.jsonl).

Usage:
    python -m eval.retrieval_runs floors eval/runs/<tag>.retrieval.jsonl
    python -m eval.retrieval_runs compare eval/runs/<a>.retrieval.jsonl eval/runs/<b>.retrieval.jsonl

floors: for a run made with --score-floor 0, the metrics at each candidate floor and the
floor the v12 rule picks (the highest one at which every question keeps 5 results).
compare: the same questions in two runs, e.g. HNSW against exact search, or two models.
"""

from __future__ import annotations

import argparse
import sys
from datetime import UTC, datetime
from pathlib import Path

from app.services.retrieval import page_key
from eval.common import read_json, read_jsonl, write_report

FLOOR_GRID = (0.3, 0.25, 0.2, 0.15, 0.1, 0.05, 0.0)
KEEP = 5  # the answer pipeline passes the top 5 to the generator


def _kept(record: dict, floor: float) -> list[dict]:
    return [r for r in record["results"] if r["score"] >= floor]


def ranked_pages_hit(record: dict, floor: float) -> tuple[list[bool], int]:
    """Per kept rank, whether its page is an expected page; and how many were kept."""
    expected = {page_key(p) for p in record["expected_source_paths"]}
    kept = _kept(record, floor)
    return [page_key(r["source_path"]) in expected for r in kept], len(kept)


def metrics(records: list[dict], floor: float = 0.0) -> dict:
    n = len(records)
    totals = {"hit@3": 0, "hit@5": 0, "hit@10": 0, "mrr": 0.0, "short": 0}
    for record in records:
        hits, kept = ranked_pages_hit(record, floor)
        for k in (3, 5, 10):
            totals[f"hit@{k}"] += any(hits[:k])
        first = next((rank for rank, hit in enumerate(hits, start=1) if hit), None)
        totals["mrr"] += 1 / first if first else 0.0
        totals["short"] += kept < KEEP
    return {
        "n": n,
        "hit@3": totals["hit@3"] / n,
        "hit@5": totals["hit@5"] / n,
        "hit@10": totals["hit@10"] / n,
        "mrr": totals["mrr"] / n,
        "short": totals["short"],
    }


def pick_floor(records: list[dict], grid: tuple[float, ...] = FLOOR_GRID) -> float:
    """The highest floor at which every question keeps KEEP results (or all it had)."""
    for floor in grid:
        if all(len(_kept(r, floor)) >= min(KEEP, len(r["results"])) for r in records):
            return floor
    return 0.0


def compare(a: list[dict], b: list[dict], top: int = 10) -> dict:
    by_id = {r["id"]: r for r in b}
    if [r["id"] for r in a] != [r["id"] for r in b]:
        raise ValueError("the two runs do not hold the same questions in the same order")
    changed, ups, downs = [], [], []
    for ra in a:
        rb = by_id[ra["id"]]
        ids_a = [r["chunk_id"] for r in ra["results"][:top]]
        ids_b = [r["chunk_id"] for r in rb["results"][:top]]
        if ids_a != ids_b:
            changed.append(ra["id"])
        rr_a, rr_b = metrics([ra])["mrr"], metrics([rb])["mrr"]
        if rr_b > rr_a:
            ups.append(ra["id"])
        elif rr_b < rr_a:
            downs.append(ra["id"])
    ma, mb = metrics(a), metrics(b)
    return {
        "n": len(a),
        "same_ranking": len(a) - len(changed),
        "changed_ids": changed,
        "rr_up": ups,
        "rr_down": downs,
        "mrr_a": ma["mrr"],
        "mrr_b": mb["mrr"],
        "hit5_a": ma["hit@5"],
        "hit5_b": mb["hit@5"],
    }


def _records(path: Path) -> list[dict]:
    return read_jsonl(path)


def _floors_report(path: Path) -> str:
    records = _records(path)
    meta = read_json(path.with_name(path.name.replace(".retrieval.jsonl", ".retrieval.meta.json")))
    floors_used = {r["score_floor"] for r in records}
    if floors_used != {0.0}:
        raise SystemExit(f"{path} was not run with --score-floor 0 (floors {floors_used})")
    lines = [
        f"# Score floors ({path.name})",
        "",
        f"- run: {meta.get('tag')}, database {meta.get('database')}, "
        f"models {meta.get('embedding_models')}",
        f"- questions: {len(records)}; 'short' = questions keeping fewer than {KEEP} results",
        "",
        "| floor | short | Hit@3 | Hit@5 | Hit@10 | MRR |",
        "|---|---|---|---|---|---|",
    ]
    for floor in FLOOR_GRID:
        m = metrics(records, floor)
        lines.append(
            f"| {floor} | {m['short']} | {m['hit@3']:.3f} | {m['hit@5']:.3f} "
            f"| {m['hit@10']:.3f} | {m['mrr']:.3f} |"
        )
    lines += ["", f"rule pick (highest floor with no short question): **{pick_floor(records)}**"]
    return "\n".join(lines)


def _compare_report(path_a: Path, path_b: Path, top: int) -> str:
    diff = compare(_records(path_a), _records(path_b), top)
    return "\n".join(
        [
            f"# Retrieval runs compared: {path_a.name} vs {path_b.name}",
            "",
            f"- questions: {diff['n']}; same top-{top} chunk ids: {diff['same_ranking']}",
            f"- ranking changed: {', '.join(diff['changed_ids']) or 'none'}",
            f"- MRR a {diff['mrr_a']:.3f} -> b {diff['mrr_b']:.3f}; "
            f"Hit@5 a {diff['hit5_a']:.3f} -> b {diff['hit5_b']:.3f}",
            f"- reciprocal rank up in b: {', '.join(diff['rr_up']) or 'none'}",
            f"- reciprocal rank down in b: {', '.join(diff['rr_down']) or 'none'}",
        ]
    )


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    floors = sub.add_parser("floors")
    floors.add_argument("run", type=Path)
    cmp = sub.add_parser("compare")
    cmp.add_argument("a", type=Path)
    cmp.add_argument("b", type=Path)
    cmp.add_argument("--top", type=int, default=10)
    args = parser.parse_args(argv)

    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    if args.command == "floors":
        report = _floors_report(args.run)
        name = f"retrieval_floors_{args.run.name.removesuffix('.retrieval.jsonl')}_{timestamp}.md"
    else:
        report = _compare_report(args.a, args.b, args.top)
        tag_a, tag_b = (p.name.removesuffix(".retrieval.jsonl") for p in (args.a, args.b))
        stem = f"{tag_a}_vs_{tag_b}"
        name = f"retrieval_compare_{stem}_{timestamp}.md"
    path = write_report(name, report)
    print(report)
    print(f"\nwritten to {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

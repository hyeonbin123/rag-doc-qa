"""Arms, gate and summaries for the generation-model comparison (docs/experiments.md v13).

Selection and adoption runs generate with the language guard on (LANGUAGE_GUARD=true).
eval/run_answer_eval.py then records the final answer and, when the guard regenerated,
the first answer too. One run therefore gives two arms:

- raw: the generator alone, i.e. the first answer call, which is what a run without the
  guard returns (same request; the guard's extra call comes after it)
- lg: the generator with the guard, i.e. the final answer

`split` writes them as <stem>.raw.gen.jsonl and <stem>.lg.gen.jsonl next to the run, so
eval/run_judge.py judges each like any other run. In the raw arm an item the guard
regenerated has no citations (the citation call saw the final answer) and its generation
time leaves out the retry.

`gate` checks a guard-off run of one candidate against the v13 smoke gate: the model fully
on the GPU, its pinned digest, no reasoning output, schema-valid citation replies on the
first 10 items, at most one answer cut by the output limit, and the generation p50.

`summary` lines up arms over the same items: J1 correctness, hallucination flags,
kana/han answers, generation p50, stop reasons, citation checks, guard counts, by
language, with paired bootstrap intervals against a baseline arm.

Usage:
    python -m eval.generator_arms split eval/runs/v13_sel_g0_qa_dev.gen.jsonl [...]
    python -m eval.generator_arms gate eval/runs/v13_gate_g1_qa_dev_ko.gen.jsonl --digest <sha256>
        [--max-p50-ms 10000] [--require-prompt-match MODEL] [--prompt-tolerance 16]
    python -m eval.generator_arms summary --tag v13_sel --label J1 --baseline G0
        --arm G0=eval/runs/v13_sel_g0_qa_dev.raw.gen.jsonl,eval/runs/v13_sel_g0_qa_dev_ko.raw.gen.jsonl
        --arm G1=... [--share G0+LG=G0]
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from datetime import UTC, datetime
from pathlib import Path

from app.services.generation import KANA_HAN_RE
from app.services.retrieval import page_key
from eval.answer_report import display_path
from eval.common import (
    REPORTS_DIR,
    keyword_coverage,
    read_json,
    read_jsonl,
    write_json,
    write_jsonl,
    write_report,
)
from eval.compare_judgments import paired_bootstrap_ci
from eval.judge import TRUNCATION_TOLERANCE, answer_sha1
from eval.run_judge import judged_path, meta_path

GATE_FIRST_ITEMS = 10
GATE_MAX_LENGTH_STOPS = 1
GATE_MAX_P50_MS = 10_000.0


def _calls(record: dict) -> list[dict]:
    return ((record.get("generation_calls") or {}).get("answer")) or []


def unguarded_record(record: dict) -> dict:
    """The raw arm: what the generator returned before the guard looked at it."""
    out = dict(record)
    calls = _calls(record)
    if record.get("guard_applied"):
        answer = record["unguarded_answer"]
        out.update(
            answer=answer,
            cited_chunk_numbers=None,  # the citation call saw the final answer
            generation_ms=record["generation_ms"] - (record.get("guard_retry_ms") or 0.0),
            keyword_coverage=keyword_coverage(answer, record.get("must_include_keywords") or []),
            kana_han=bool(KANA_HAN_RE.search(answer)),
        )
    out["answer_done_reason"] = calls[0]["done_reason"] if calls else None
    out["arm"] = "raw"
    return out


def guarded_record(record: dict) -> dict:
    """The lg arm: the final answer, as the app with the guard on would return it."""
    out = dict(record)
    calls = _calls(record)
    out["answer_done_reason"] = calls[-1]["done_reason"] if calls else None
    out["arm"] = "lg"
    return out


def _arm_path(gen_path: Path, arm: str) -> Path:
    stem = gen_path.name.removesuffix(".jsonl").removesuffix(".gen")
    return gen_path.with_name(f"{stem}.{arm}.gen.jsonl")


def split_file(gen_path: Path) -> tuple[Path, Path]:
    meta = read_json(meta_path(gen_path))
    if not meta.get("language_guard"):
        raise ValueError(f"{gen_path.name} was generated without the language guard; there is one arm only")
    records = read_jsonl(gen_path)
    paths = []
    for arm, derive in (("raw", unguarded_record), ("lg", guarded_record)):
        out = _arm_path(gen_path, arm)
        # The arm goes into the run tag, so the two arms' judge reports never share a name.
        write_jsonl(out, [{**derive(r), "run_tag": f"{r.get('run_tag')}.{arm}"} for r in records])
        write_json(meta_path(out), {**meta, "arm": arm, "derived_from": display_path(gen_path)})
        paths.append(out)
    return paths[0], paths[1]


# --- per-item metrics ------------------------------------------------------------------


def _thinking(record: dict) -> bool:
    calls = record.get("generation_calls") or {}
    every = [*(calls.get("answer") or []), *([calls["citation"]] if calls.get("citation") else [])]
    return bool(record.get("think_tag_in_answer")) or any((c.get("thinking_chars") or 0) > 0 for c in every)


def item_row(record: dict, judgment: dict | None) -> dict:
    j = judgment or {}
    cited = record.get("cited_chunk_numbers")
    chunks = record.get("chunks") or []
    in_range = cites_expected = None
    if cited is not None:
        in_range = bool(cited) and all(isinstance(n, int) and 1 <= n <= len(chunks) for n in cited)
        expected = {page_key(p) for p in record.get("expected_source_paths") or []}
        cites_expected = any(
            isinstance(n, int)
            and 1 <= n <= len(chunks)
            and page_key(chunks[n - 1]["source_path"]) in expected
            for n in cited
        )
    return {
        "dataset": record.get("dataset"),
        "id": record["id"],
        "language": record.get("language"),
        "arm": record.get("arm"),
        "correctness": j.get("correctness_score"),
        "faithfulness": j.get("faithfulness_score"),
        "hallucinated": j.get("hallucinated"),
        "judged": j.get("correctness_score") is not None,
        "kana_han": bool(record.get("kana_han")),
        "generation_ms": record.get("generation_ms"),
        "done_length": record.get("answer_done_reason") == "length",
        "thinking": _thinking(record),
        "citation_error": record.get("citation_schema_error") is not None if cited is not None else None,
        "citations_in_range": in_range,
        "cites_expected_page": cites_expected,
        "guard_applied": bool(record.get("guard_applied")),
        "guard_retry_ms": record.get("guard_retry_ms"),
        "answer_sha1": answer_sha1(record.get("answer") or ""),
    }


def _ratio(values: list) -> str:
    known = [v for v in values if v is not None]
    return f"{sum(1 for v in known if v)}/{len(known)}"


def _summary(rows: list[dict]) -> dict:
    judged = [r for r in rows if r["judged"]]
    times = [r["generation_ms"] for r in rows if r["generation_ms"] is not None]
    retries = [r["guard_retry_ms"] for r in rows if r.get("guard_retry_ms") is not None]
    return {
        "n": len(rows),
        "judged": len(judged),
        "correctness_sum": sum(r["correctness"] for r in judged),
        "faithfulness_sum": sum(r["faithfulness"] for r in judged),
        "hallucinated": sum(1 for r in judged if r["hallucinated"]),
        "kana_han": sum(1 for r in rows if r["kana_han"]),
        "generation_p50_ms": statistics.median(times) if times else None,
        "done_length": sum(1 for r in rows if r["done_length"]),
        "thinking": sum(1 for r in rows if r["thinking"]),
        "citation_errors": sum(1 for r in rows if r["citation_error"]),
        "citations_in_range": _ratio([r["citations_in_range"] for r in rows]),
        "cites_expected_page": _ratio([r["cites_expected_page"] for r in rows]),
        "guard_applied": sum(1 for r in rows if r["guard_applied"]),
        "guard_retry_p50_ms": statistics.median(retries) if retries else None,
    }


def summarize(rows: list[dict]) -> dict:
    return {
        "all": _summary(rows),
        "en": _summary([r for r in rows if r["language"] == "en"]),
        "ko": _summary([r for r in rows if r["language"] == "ko"]),
    }


def arm_rows(gen_paths: list[Path], label: str | None) -> list[dict]:
    rows = []
    for gen_path in gen_paths:
        judgments = {}
        if label:
            judged = judged_path(gen_path, label)
            if judged.exists():
                judgments = {j["id"]: j for j in read_jsonl(judged)}
        records = sorted(read_jsonl(gen_path), key=lambda r: r.get("dataset_index") or 0)
        rows += [item_row(r, judgments.get(r["id"])) for r in records]
    return rows


# --- the smoke gate --------------------------------------------------------------------


def _loaded(meta: dict) -> dict | None:
    for m in (meta.get("ollama_ps_after") or {}).get("models", []):
        if m.get("name") == meta.get("model") or m.get("model") == meta.get("model"):
            return m
    return None


def gate(
    gen_path: Path,
    *,
    digest: str | None,
    max_p50_ms: float = GATE_MAX_P50_MS,
    require_prompt_match: bool = False,
    prompt_tolerance: int = TRUNCATION_TOLERANCE,
) -> dict:
    meta = read_json(meta_path(gen_path))
    records = sorted(read_jsonl(gen_path), key=lambda r: r.get("dataset_index") or 0)
    rows = [item_row(guarded_record(r), None) for r in records]
    loaded = _loaded(meta)
    first = rows[:GATE_FIRST_ITEMS]
    p50 = statistics.median(r["generation_ms"] for r in rows)
    diffs = [
        _calls(r)[0]["prompt_eval_count"] - r["generation_prompt_tokens_counted"]
        for r in records
        if _calls(r)
        and r.get("generation_prompt_tokens_counted") is not None
        and _calls(r)[0].get("prompt_eval_count") is not None
    ]
    checks = {
        "full_gpu": {
            "ok": bool(loaded)
            and loaded.get("size_vram") == loaded.get("size")
            and loaded.get("context_length") in (None, 8192),
            "value": {k: (loaded or {}).get(k) for k in ("size", "size_vram", "context_length")},
        },
        "digest": {
            "ok": digest is None or meta.get("model_digest") == digest,
            "value": meta.get("model_digest"),
        },
        "no_thinking": {
            "ok": not any(r["thinking"] for r in rows),
            "value": sum(r["thinking"] for r in rows),
        },
        "citations_first_10": {
            "ok": len(first) == GATE_FIRST_ITEMS and not any(r["citation_error"] for r in first),
            "value": f"{sum(1 for r in first if not r['citation_error'])}/{len(first)} valid "
            f"({sum(1 for r in rows if r['citation_error'])} invalid in all {len(rows)})",
        },
        "done_length": {
            "ok": sum(r["done_length"] for r in rows) <= GATE_MAX_LENGTH_STOPS,
            "value": sum(r["done_length"] for r in rows),
        },
        "p50": {"ok": p50 <= max_p50_ms, "value": round(p50, 1)},
    }
    prompt_count = {
        "items": len(diffs),
        "max_abs_diff": max((abs(d) for d in diffs), default=None),
        "median_diff": statistics.median(diffs) if diffs else None,
    }
    if require_prompt_match:
        checks["prompt_match"] = {
            "ok": len(diffs) == len(records) and all(abs(d) <= prompt_tolerance for d in diffs),
            "value": prompt_count,
        }
    return {
        "run": display_path(gen_path),
        "model": meta.get("model"),
        "think": meta.get("think"),
        "language_guard": meta.get("language_guard"),
        "questions": len(rows),
        "passed": all(c["ok"] for c in checks.values()),
        "checks": checks,
        "prompt_count": prompt_count,
    }


# --- reports ---------------------------------------------------------------------------


def _ci_cell(base: list[dict], other: list[dict], language: str | None) -> str:
    by_key = {(r["dataset"], r["id"]): r for r in other}
    diffs = []
    for r in base:
        o = by_key.get((r["dataset"], r["id"]))
        if o and r["judged"] and o["judged"] and (language is None or r["language"] == language):
            diffs.append(o["correctness"] - r["correctness"])
    if not diffs:
        return "n/a"
    mean, low, high = paired_bootstrap_ci(diffs)
    return f"{sum(diffs):+d} ({mean:+.3f} [{low:+.3f}, {high:+.3f}])"


def _answers_differ(base: list[dict], other: list[dict]) -> int:
    by_key = {(r["dataset"], r["id"]): r["answer_sha1"] for r in other}
    return sum(1 for r in base if by_key.get((r["dataset"], r["id"])) != r["answer_sha1"])


JUDGMENT_FIELDS = ("correctness", "faithfulness", "hallucinated", "judged")


def share_unguarded_judgments(lg_rows: list[dict], raw_rows: list[dict], raw_name: str) -> dict:
    """Give the lg arm the raw arm's judgment wherever the guard did not fire.

    Those answers are the same text in both arms, yet J1 can score the same answer a point
    apart when it sits at another place in the judge order (docs/experiments.md v13, rule
    change 2026-10-05). Sharing keeps that noise out of the guard's effect; the lg arm's own
    differing judgments are only counted.
    """
    by_key = {(r["dataset"], r["id"]): r for r in raw_rows}
    shared = differs = 0
    for row in lg_rows:
        raw = by_key.get((row["dataset"], row["id"]))
        if raw is None or row["guard_applied"]:
            continue
        if any(row[f] != raw[f] for f in JUDGMENT_FIELDS):
            differs += 1
        row.update({f: raw[f] for f in JUDGMENT_FIELDS})
        shared += 1
    return {"from": raw_name, "items": shared, "own_judgment_differs": differs}


def summary_report(
    tag: str,
    label: str,
    arms: dict[str, list[Path]],
    baseline: str | None,
    shares: dict[str, str] | None = None,
) -> tuple[str, dict]:
    rows = {name: arm_rows(paths, label) for name, paths in arms.items()}
    data = {"tag": tag, "label": label, "baseline": baseline, "arms": {}}
    shared_notes = {}
    for lg_name, raw_name in (shares or {}).items():
        shared_notes[lg_name] = share_unguarded_judgments(rows[lg_name], rows[raw_name], raw_name)
    lines = [
        f"# Generator comparison ({tag}, judge {label})",
        "",
        f"- date: {datetime.now(UTC).isoformat()}",
        *[f"- {name}: {', '.join(display_path(p) for p in paths)}" for name, paths in arms.items()],
        "- correctness/faithfulness: J1 sums over judged items; kana/han: answers with kana or Han anywhere",
        "- citations: replies that break the schema; cited numbers within 1..k; a cited passage on an "
        "expected page (raw-arm items the guard regenerated have no citations of their own and are left out)",
        *[
            f"- {lg}: items the guard left alone take {n['from']}'s judgment ({n['items']} items; "
            f"its own judgment differed on {n['own_judgment_differs']})"
            for lg, n in shared_notes.items()
        ],
        "",
        "| arm | lang | n | correctness sum | hallucinated | kana/han | faithfulness sum | gen p50 ms "
        "| done=length | thinking | citation errors | cites in range | cites expected page | guard applied "
        "| guard retry p50 ms |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for name, arm in rows.items():
        s = summarize(arm)
        data["arms"][name] = {"summary": s, "files": [display_path(p) for p in arms[name]], "rows": arm}
        if name in shared_notes:
            data["arms"][name]["shared"] = shared_notes[name]
        for lang in ("en", "ko", "all"):
            x = s[lang]
            if not x["n"]:
                continue
            p50 = "n/a" if x["generation_p50_ms"] is None else f"{x['generation_p50_ms']:.0f}"
            retry = "-" if x["guard_retry_p50_ms"] is None else f"{x['guard_retry_p50_ms']:.0f}"
            lines.append(
                f"| {name} | {lang} | {x['n']} | {x['correctness_sum']} ({x['judged']} judged) "
                f"| {x['hallucinated']} | {x['kana_han']} | {x['faithfulness_sum']} | {p50} "
                f"| {x['done_length']} | {x['thinking']} "
                f"| {x['citation_errors']} | {x['citations_in_range']} | {x['cites_expected_page']} "
                f"| {x['guard_applied']} | {retry} |"
            )
    if baseline:
        lines += [
            "",
            f"## Correctness against {baseline} (sum of per-item differences, mean [paired bootstrap 90%])",
            "",
            "| arm | en | ko | all | answers differ |",
            "|---|---|---|---|---|",
        ]
        base = rows[baseline]
        for name, arm in rows.items():
            if name == baseline:
                continue
            cells = [_ci_cell(base, arm, lang) for lang in ("en", "ko", None)]
            lines.append(f"| {name} | {' | '.join(cells)} | {_answers_differ(base, arm)} |")
            data["arms"][name]["vs_baseline"] = dict(zip(("en", "ko", "all"), cells, strict=True))
    return "\n".join(lines), data


def gate_report(results: list[dict]) -> str:
    # Runs can have different checks (only the A.X run checks its prompt counts), so the
    # columns are every check any run has; a run without one gets "-" there.
    names = list(dict.fromkeys(name for r in results for name in r["checks"]))
    lines = [
        "# Generation smoke gate (docs/experiments.md v13)",
        "",
        f"- date: {datetime.now(UTC).isoformat()}",
        f"- first {GATE_FIRST_ITEMS} citation replies schema-valid, "
        f"done_reason=length <= {GATE_MAX_LENGTH_STOPS}, no reasoning output, "
        "model fully on the GPU (size_vram == size), pinned digest, p50 limit",
        "",
        "| run | model | think | passed | " + " | ".join(names) + " | prompt count Ollama - tokenizer |",
        "|---|---|---|---|" + "---|" * len(names) + "---|",
    ]
    for r in results:
        cells = [
            f"{'ok' if r['checks'][name]['ok'] else 'FAIL'}: {r['checks'][name]['value']}"
            if name in r["checks"]
            else "-"
            for name in names
        ]
        pc = r["prompt_count"]
        lines.append(
            f"| {r['run']} | {r['model']} | {r['think']} | {r['passed']} | {' | '.join(cells)} "
            f"| {pc['items']} items, median {pc['median_diff']}, max abs {pc['max_abs_diff']} |"
        )
    return "\n".join(lines)


def _write(name: str, report: str, data: dict | list) -> Path:
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    path = write_report(f"{name}_{timestamp}.md", report)
    (REPORTS_DIR / f"{name}_{timestamp}.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    return path


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sp = sub.add_parser("split")
    sp.add_argument("paths", type=Path, nargs="+")
    gp = sub.add_parser("gate")
    gp.add_argument("paths", type=Path, nargs="+")
    gp.add_argument("--tag", required=True)
    gp.add_argument("--digest", action="append", default=[], help="model=sha256, one per model")
    gp.add_argument("--max-p50-ms", type=float, default=GATE_MAX_P50_MS)
    gp.add_argument(
        "--require-prompt-match", action="append", default=[], help="model whose counts must agree"
    )
    gp.add_argument(
        "--prompt-tolerance",
        type=int,
        default=TRUNCATION_TOLERANCE,
        help="allowed |Ollama - tokenizer| tokens",
    )
    su = sub.add_parser("summary")
    su.add_argument("--tag", required=True)
    su.add_argument("--label", default="J1")
    su.add_argument("--baseline", default=None)
    su.add_argument("--arm", action="append", required=True, help="NAME=gen1,gen2,...")
    su.add_argument(
        "--share",
        action="append",
        default=[],
        help="LG=RAW: the LG arm takes RAW's judgment where the guard did not fire",
    )
    args = parser.parse_args()
    sys.stdout.reconfigure(errors="backslashreplace")  # see eval/run_answer_eval.py

    if args.command == "split":
        for path in args.paths:
            raw, lg = split_file(path)
            print(f"{path.name} -> {raw.name}, {lg.name}")
        return 0
    if args.command == "gate":
        digests = dict(d.split("=", 1) for d in args.digest)
        results = []
        for path in args.paths:
            model = read_json(meta_path(path)).get("model")
            results.append(
                gate(
                    path,
                    digest=digests.get(model),
                    max_p50_ms=args.max_p50_ms,
                    require_prompt_match=model in args.require_prompt_match,
                    prompt_tolerance=args.prompt_tolerance,
                )
            )
        report = gate_report(results)
        path = _write(f"generator_gate_{args.tag}", report, results)
        print(report)
        print(f"\nwritten to {path}")
        return 0 if all(r["passed"] for r in results) else 1
    arms = {}
    for spec in args.arm:
        name, files = spec.split("=", 1)
        arms[name] = [Path(f) for f in files.split(",") if f]
    shares = dict(spec.split("=", 1) for spec in args.share)
    report, data = summary_report(args.tag, args.label, arms, args.baseline, shares)
    path = _write(f"generator_summary_{args.tag}", report, data)
    print(report)
    print(f"\nwritten to {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

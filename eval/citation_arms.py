"""인용 호출 단축 비교(docs/experiments.md v15 I3): 지금 방식(A, separate)과 이어 붙이기 방식(B, followup).

사용법:
    python -m eval.citation_arms decide --tag v15_i3 --label J1 \
        --a eval/runs/v15_i3_a_qa_dev.gen.jsonl ... --b eval/runs/v15_i3_b_qa_dev.gen.jsonl ...
"""

# [파일 역할] v15 I3의 결정기. 같은 세션에서 셋마다 A → B 순서로 생성한 기록을 문항 단위로 맞춰, 측정 전에
# 등록한 네 조건(생성 시간, 인용 적중, 인용 스키마, 답 글·정확도)을 계산하고 채택 여부를 낸다.
# [왜 이렇게 세나]
# - 답변 호출은 두 방식이 같으므로 답 글은 대부분 같아야 한다. 같은 답이면 판정도 같아야 하므로, 답이 같은
#   문항은 A의 판정을 B에도 쓴다(판정 흔들림이 비교에 섞이지 않게, v13 규칙 변경 fbd1b80과 같은 생각). 답이
#   다른 문항만 B 자기 판정을 쓴다.
# - 인용 적중은 '생성 컨텍스트에 정답 페이지가 있었던 문항 중 정답 페이지 청크를 인용한 문항 수'다
#   (eval/generator_arms.py의 cites_expected_page와 같은 정의).
# [연결] 행 만들기는 eval/generator_arms.py의 arm_rows를 그대로 쓴다.

from __future__ import annotations

import argparse
import statistics
import sys
from datetime import UTC, datetime
from pathlib import Path

from eval.common import read_jsonl, write_json, write_report
from eval.generator_arms import arm_rows

# 등록한 조건의 기준값(docs/experiments.md v15 I3).
MIN_SPEEDUP_MS = 1000.0  # 조건 1: 생성 중앙값이 A보다 1초 이상 짧아야 함
CITE_TOLERANCE = 1  # 조건 2: 인용 적중 문항 수 B ≥ A − 1
JUDGE_TOLERANCE = 2  # 조건 4: 답이 다른 문항이 있으면 정확도 합 B ≥ A − 2


# 기록에서 인용 호출의 시간·토큰 수를 꺼낸다(보고용). 인용 호출이 없던 문항은 None.
def _citation_call(record: dict) -> dict | None:
    calls = record.get("generation_calls") or {}
    return calls.get("citation")


def _median(values: list) -> float | None:
    known = [v for v in values if v is not None]
    return statistics.median(known) if known else None


# A와 B의 생성 기록·판정을 문항 단위로 맞춰 조건을 계산한다. label은 결정에 쓰는 판정 라벨(I2가 정한 방식).
def decide(a_paths: list[Path], b_paths: list[Path], label: str) -> dict:
    a_rows = {(r["dataset"], r["id"]): r for r in arm_rows(a_paths, label)}
    b_rows = {(r["dataset"], r["id"]): r for r in arm_rows(b_paths, label)}
    if set(a_rows) != set(b_rows):
        raise ValueError("arms A and B must cover the same items")
    a_recs = {(r["dataset"], r["id"]): r for p in a_paths for r in read_jsonl(p)}
    b_recs = {(r["dataset"], r["id"]): r for p in b_paths for r in read_jsonl(p)}

    same_answer = [k for k in a_rows if a_rows[k]["answer_sha1"] == b_rows[k]["answer_sha1"]]
    differ = sorted(k[1] for k in a_rows if k not in set(same_answer))
    # 공유 규칙: 답이 같으면 B 판정 = A 판정. 다르면 각자 자기 판정.
    a_sum = sum(r["correctness"] or 0 for r in a_rows.values())
    b_sum = sum(
        (a_rows[k]["correctness"] if k in same_answer else b_rows[k]["correctness"]) or 0 for k in b_rows
    )
    unjudged_differ = [k[1] for k in b_rows if k not in same_answer and not b_rows[k]["judged"]]

    def arm_stats(rows: dict, recs: dict) -> dict:
        calls = [_citation_call(recs[k]) for k in rows]
        return {
            "generation_p50_ms": _median([r["generation_ms"] for r in rows.values()]),
            "generation_p50_ms_en": _median(
                [r["generation_ms"] for r in rows.values() if r["language"] == "en"]
            ),
            "generation_p50_ms_ko": _median(
                [r["generation_ms"] for r in rows.values() if r["language"] == "ko"]
            ),
            "citation_call_p50_ms": _median([c.get("ms") for c in calls if c]),
            "citation_prompt_tokens_p50": _median([c.get("prompt_eval_count") for c in calls if c]),
            "citation_output_tokens_p50": _median([c.get("eval_count") for c in calls if c]),
            "cites_expected": sum(
                1 for r in rows.values() if r["context_has_expected_page"] and r["cites_expected_page"]
            ),
            "context_has_expected": sum(1 for r in rows.values() if r["context_has_expected_page"]),
            "schema_errors": sum(1 for r in rows.values() if r["citation_error"]),
            "empty_citations": sum(1 for k in rows if not recs[k].get("cited_chunk_numbers")),
            "kana_han": sum(1 for r in rows.values() if r["kana_han"]),
        }

    a_stats, b_stats = arm_stats(a_rows, a_recs), arm_stats(b_rows, b_recs)
    conditions = {
        "1_latency": b_stats["generation_p50_ms"] <= a_stats["generation_p50_ms"] - MIN_SPEEDUP_MS,
        "2_citation_hits": b_stats["cites_expected"] >= a_stats["cites_expected"] - CITE_TOLERANCE,
        "3_schema": b_stats["schema_errors"] == 0 and b_stats["empty_citations"] == 0,
        "4_answers": (not differ) or (not unjudged_differ and b_sum >= a_sum - JUDGE_TOLERANCE),
    }
    return {
        "label": label,
        "n": len(a_rows),
        "same_answer": len(same_answer),
        "answers_differ_ids": differ,
        "correctness_sum": {"A": a_sum, "B_shared": b_sum},
        "A": a_stats,
        "B": b_stats,
        "conditions": conditions,
        "adopt": all(conditions.values()),
    }


def render(tag: str, result: dict) -> str:
    a, b = result["A"], result["B"]
    rows = [
        ("생성 중앙값 ms (답변+가드+인용)", a["generation_p50_ms"], b["generation_p50_ms"]),
        ("  영어", a["generation_p50_ms_en"], b["generation_p50_ms_en"]),
        ("  한국어", a["generation_p50_ms_ko"], b["generation_p50_ms_ko"]),
        ("인용 호출 중앙값 ms", a["citation_call_p50_ms"], b["citation_call_p50_ms"]),
        ("인용 호출 프롬프트 토큰 중앙값", a["citation_prompt_tokens_p50"], b["citation_prompt_tokens_p50"]),
        ("인용 호출 출력 토큰 중앙값", a["citation_output_tokens_p50"], b["citation_output_tokens_p50"]),
        (
            "인용 적중 / 컨텍스트에 정답 페이지",
            f"{a['cites_expected']}/{a['context_has_expected']}",
            f"{b['cites_expected']}/{b['context_has_expected']}",
        ),
        ("인용 스키마 오류", a["schema_errors"], b["schema_errors"]),
        ("빈 인용", a["empty_citations"], b["empty_citations"]),
        ("섞인 답", a["kana_han"], b["kana_han"]),
    ]
    lines = [
        f"# 인용 호출 단축 비교 {tag}",
        "",
        f"- 문항 {result['n']}, 답 글이 같은 문항 {result['same_answer']}, 다른 문항: "
        f"{', '.join(result['answers_differ_ids']) or '없음'}",
        f"- 정확도 합 ({result['label']}, 같은 답은 A 판정 공유): A {result['correctness_sum']['A']}, "
        f"B {result['correctness_sum']['B_shared']}",
        "",
        "| 지표 | A (separate) | B (followup) |",
        "|---|---|---|",
        *[f"| {name} | {x} | {y} |" for name, x, y in rows],
        "",
        "| 조건 | 결과 |",
        "|---|---|",
        *[f"| {k} | {'만족' if v else '떨어짐'} |" for k, v in result["conditions"].items()],
        "",
        f"**결정: {'채택 (CITATION_MODE=followup)' if result['adopt'] else '채택 안 함 (separate 유지)'}**",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="v15 I3 인용 호출 단축 비교의 결정기")
    sub = parser.add_subparsers(dest="command", required=True)
    dp = sub.add_parser("decide")
    dp.add_argument("--tag", required=True)
    dp.add_argument("--label", required=True, help="결정에 쓰는 판정 라벨(I2 결과의 방식)")
    dp.add_argument("--a", type=Path, nargs="+", required=True, help="A(separate) 생성 기록들")
    dp.add_argument("--b", type=Path, nargs="+", required=True, help="B(followup) 생성 기록들, A와 같은 순서")
    args = parser.parse_args()
    result = decide(args.a, args.b, args.label)
    stamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    write_json(Path("eval/runs") / f"{args.tag}.decision.json", {"tag": args.tag, **result})
    path = write_report(f"citation_arms_{args.tag}_{stamp}.md", render(args.tag, result))
    print(f"adopt={result['adopt']} conditions={result['conditions']}; report {path}")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(errors="backslashreplace")
    sys.exit(main())

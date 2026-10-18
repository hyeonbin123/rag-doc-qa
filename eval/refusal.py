"""답 없는 질문의 거절과 언어별 바닥값(docs/experiments.md v15 I4).

사용법:
    # dev: 바닥값 0으로 돌린 검색 기록에서 언어별 바닥값 후보를 고른다(CPU)
    python -m eval.refusal floors --tag v15_i4_floors \
        --answerable <답 있는 dev 검색 기록 ...> --unanswerable <답 없는 dev 검색 기록 ...>

    # 고른 바닥값으로 문맥(상위 5개)이 바뀌는 문항 id를 언어별 파일로 쓴다(다시 생성할 문항)
    python -m eval.refusal changed --floors eval/runs/v15_i4_floors.json --out <ids.txt> \
        <retrieval.jsonl ...>

    # dev: 거절 답의 인용 비우기(c)를 고르는 조건
    python -m eval.refusal dev --tag v15_i4_dev --label J1 \
        --answerable <gen.jsonl ...> --unanswerable <gen.jsonl ...>

    # test: 기준(지금 기본값)과 후보(바닥값 + 청크 0개 거절)를 비교해 채택 여부를 낸다
    python -m eval.refusal test --tag v15_i4_test --label J1 --floors eval/runs/v15_i4_floors.json \
        --base-na <gen ...> --cand-na <gen ...> --base-ans <gen ...> --cand-ans <gen ...> \
        --used-retrieval <retrieval.jsonl ...> --c-adopted true|false
"""

# [파일 역할] v15 I4의 분석·결정기. 답 없는 질문(문서가 다루지 않는 질문)에서 시스템이 모른다고 하는지
# (거절률)를 세고, 측정 전에 등록한 규칙대로 세 후보를 고른다.
#   (a) 언어별 dense 바닥값: 지금 0.3은 한국어 granite 점수(0.8~0.95에 몰림)와 영어 bge 점수에서 한 번도
#       청크를 거르지 않았다(v14 검색 기록의 최저 점수 한국어 0.805, 영어 0.535).
#   (b) 청크가 0개면 LLM 없이 고정 거절문(app/services/generation.py의 REFUSE_WITHOUT_CONTEXT).
#   (c) 거절 답에는 인용을 붙이지 않음(EMPTY_CITATIONS_ON_REFUSAL).
# [핵심 정의]
# - 앱의 dense 검색은 상위 top_k개를 뽑은 뒤 바닥값 미만을 버린다(app/services/retrieval.py). 그래서 바닥값
#   f의 효과는 '바닥값 0으로 뽑은 상위 5개 중 점수 ≥ f인 것'으로 정확히 다시 계산된다(검색을 다시 돌리지
#   않아도 됨).
# - '정답 손실': 상위 5개에 정답 페이지(번역 무관) 청크가 있었는데 바닥값 뒤에는 하나도 남지 않은 문항.
# - 거절은 is_refusal_answer(첫 문장 정규식)로 센다. 생성 기록의 refusal 필드가 그 값이다.
# [연결] 검색 기록은 eval/run_retrieval_eval.py, 생성 기록은 eval/run_answer_eval.py, 판정은
# eval/run_judge.py가 쓴다.

from __future__ import annotations

import argparse
import math
import sys
from datetime import UTC, datetime
from pathlib import Path

from app.services.generation import is_refusal_answer
from app.services.retrieval import SCORE_FLOOR, page_key
from eval.common import read_json, read_jsonl, write_json, write_report
from eval.run_judge import judged_path

# 앱이 답변에 쓰는 상위 개수(/query/ask 기본 top_k, 평가의 --top-k 5).
CONTEXT_K = 5
# 등록한 기준값(docs/experiments.md v15 I4).
MAX_LOST = 1  # (a) 언어별 정답 손실 허용 문항 수 (dev와 test 모두)
MAX_FALSE_REFUSALS = 1  # (c) 언어별 '잘 답했는데 거절로 분류된' 답 허용 수 (dev)
GOOD_ANSWER_MIN = 4  # (c) '잘 답했다'의 판정 정확도 하한
MIN_REFUSAL_GAIN = 3  # 채택 조건 F1: 답 없는 test 질문의 거절 수가 기준보다 이만큼 이상 늘어야 함
JUDGE_TOLERANCE = 2  # 채택 조건 F3: 문맥이 바뀐 답 있는 문항의 정확도 합 허용 폭
# 청크가 0개라 판정이 없는 답 있는 문항은 가장 나쁜 점수로 센다(거절이 정답일 수 없으므로).
UNJUDGED_SCORE = 1


# 검색 기록 한 줄에서 앱이 답변에 쓸 상위 5개의 점수 목록.
def top_scores(record: dict, k: int = CONTEXT_K) -> list[float]:
    return [r["score"] for r in record["results"][:k]]


# 정답 페이지 청크의 상위 5개 안 최고 점수(없으면 None). 이 값보다 높은 바닥값이면 정답이 사라진다.
def best_gold_score(record: dict, k: int = CONTEXT_K) -> float | None:
    expected = {page_key(p) for p in record.get("expected_source_paths") or []}
    scores = [r["score"] for r in record["results"][:k] if page_key(r["source_path"]) in expected]
    return max(scores) if scores else None


# 바닥값 f를 적용했을 때 한 문항의 문맥: 남는 청크 수, 바뀌었는지, 정답을 잃었는지.
def floor_effect(record: dict, floor: float, k: int = CONTEXT_K) -> dict:
    scores = top_scores(record, k)
    kept = [s for s in scores if s >= floor]
    gold = best_gold_score(record, k)
    return {
        "kept": len(kept),
        "changed": len(kept) < len(scores),
        "zero": not kept,
        "lost": gold is not None and gold < floor,
    }


# 소수 셋째 자리에서 내림. 고른 바닥값이 기준 문항의 점수보다 커지지 않게(그 문항이 남게) 한다.
def floor3(value: float) -> float:
    return math.floor(value * 1000) / 1000


# 한 언어의 바닥값 후보를 고른다(등록한 규칙). 답 있는 문항의 '정답 최고 점수'를 오름차순으로 놓고, 정답
# 손실이 MAX_LOST개 이하인 가장 높은 값 = (MAX_LOST+1)번째로 작은 정답 점수(셋째 자리 내림)다. 지금
# 바닥값(0.3)보다 낮으면 0.3을 둔다. 정답이 상위 5개에 있는 문항이 MAX_LOST개 이하면 고르지 않는다(None).
def choose_floor(answerable: list[dict], base: float = SCORE_FLOOR, max_lost: int = MAX_LOST) -> float | None:
    golds = sorted(g for g in (best_gold_score(r) for r in answerable) if g is not None)
    if len(golds) <= max_lost:
        return None
    return max(base, floor3(golds[max_lost]))


# 바닥값 f에서 한 묶음(답 있는 / 답 없는 문항)의 효과를 센다.
def summarize_effects(records: list[dict], floor: float) -> dict:
    effects = [floor_effect(r, floor) for r in records]
    return {
        "n": len(records),
        "zero_chunks": sum(e["zero"] for e in effects),
        "context_changed": sum(e["changed"] for e in effects),
        "gold_lost": sum(e["lost"] for e in effects),
        "top1_scores": sorted(round(top_scores(r)[0], 4) for r in records if r["results"]),
    }


# floors 명령: 언어마다 바닥값을 고르고, 답 없는 dev 질문 중 그 바닥값으로 청크가 0개가 되는 문항이 하나라도
# 있을 때만 그 언어의 후보로 둔다(효과가 없는 바닥값은 바꾸지 않음). 결과는 JSON(언어 → 바닥값 또는 None).
def floors_command(answerable: list[dict], unanswerable: list[dict]) -> dict:
    out: dict = {"base_floor": SCORE_FLOOR, "languages": {}}
    for language in sorted({r["language"] for r in answerable + unanswerable}):
        ans = [r for r in answerable if r["language"] == language]
        na = [r for r in unanswerable if r["language"] == language]
        floor = choose_floor(ans)
        entry: dict = {"chosen": floor, "base": summarize_effects(ans, SCORE_FLOOR)}
        if floor is not None:
            entry["answerable"] = summarize_effects(ans, floor)
            entry["unanswerable"] = summarize_effects(na, floor)
            entry["effective"] = entry["unanswerable"]["zero_chunks"] >= 1
        else:
            entry["effective"] = False
        entry["unanswerable_base"] = summarize_effects(na, SCORE_FLOOR)
        out["languages"][language] = entry
    out["candidate_floors"] = {lang: e["chosen"] for lang, e in out["languages"].items() if e["effective"]}
    return out


# 고른 바닥값으로 문맥이 바뀌는 문항 id(다시 생성할 문항). 후보 바닥값이 없는 언어의 문항은 바뀌지 않는다.
def changed_ids(records: list[dict], floors: dict[str, float]) -> list[str]:
    return [
        r["id"]
        for r in records
        if r["language"] in floors and floor_effect(r, floors[r["language"]])["changed"]
    ]


# 생성 기록 + 같은 라벨의 판정을 (데이터셋, id) → (기록, 판정) 사전으로 읽는다.
def load_answers(gen_paths: list[Path], label: str | None) -> dict[tuple[str, str], tuple[dict, dict | None]]:
    out = {}
    for gen in gen_paths:
        judgments = {}
        if label and judged_path(gen, label).exists():
            judgments = {j["id"]: j for j in read_jsonl(judged_path(gen, label))}
        for r in read_jsonl(gen):
            out[(r["dataset"], r["id"])] = (r, judgments.get(r["id"]))
    return out


# 기록의 거절 여부. 생성 기록의 refusal 필드는 생성할 때의 분류기 값이므로 쓰지 않고, 지금 분류기로 답을 다시
# 분류한다. 2026-10-18 분류기 보강(docs/experiments.md v15 규칙 변경) 뒤에도 dev와 test, 두 팔이 같은 분류기로
# 세어지게 하려는 것이다.
def refused(record: dict) -> bool:
    return is_refusal_answer(record["answer"], record.get("language", "en"))


# dev 명령: (c) 거절 답의 인용 비우기를 고르는 조건. 답 있는 dev 답 중 '판정 정확도 ≥ 4인데 거절로 분류된'
# 답이 언어별 MAX_FALSE_REFUSALS 이하이면 (c)를 test 후보에 넣는다. 답 없는 dev 질문의 거절 수와 거절인데
# 인용이 붙은 답 수는 보고한다.
def dev_command(answerable: dict, unanswerable: dict) -> dict:
    out: dict = {"languages": {}}
    for language in sorted(
        {r["language"] for r, _ in list(answerable.values()) + list(unanswerable.values())}
    ):
        ans = [(r, j) for r, j in answerable.values() if r["language"] == language]
        na = [(r, j) for r, j in unanswerable.values() if r["language"] == language]
        false_refusals = [
            r["id"]
            for r, j in ans
            if refused(r) and j and (j.get("correctness_score") or 0) >= GOOD_ANSWER_MIN
        ]
        out["languages"][language] = {
            "answerable_n": len(ans),
            "answerable_refusals": sum(refused(r) for r, _ in ans),
            "false_refusals": false_refusals,
            "unanswerable_n": len(na),
            "unanswerable_refusals": sum(refused(r) for r, _ in na),
            "refusals_with_citations": sum(
                1 for r, _ in na + ans if refused(r) and r.get("cited_chunk_numbers")
            ),
        }
    out["c_adopted_for_test"] = all(
        len(e["false_refusals"]) <= MAX_FALSE_REFUSALS for e in out["languages"].values()
    )
    return out


# 후보 팔의 문항: 다시 생성한 문항은 후보 기록, 아니면 기준 기록(문맥이 같으므로 같은 요청, 공유 규칙).
def merge_candidate(base: dict, cand: dict) -> dict:
    return {key: cand.get(key, value) for key, value in base.items()}


# test 명령: 등록한 채택 조건 F1~F4와 (c)의 효과를 센다.
# - F1: 답 없는 test 질문의 거절 수 후보 ≥ 기준 + MIN_REFUSAL_GAIN (두 언어 합)
# - F2: 이미 쓴 답 있는 test 셋들의 검색 기록에서, 고른 바닥값의 정답 손실 ≤ MAX_LOST (언어별)
# - F3: 문맥이 바뀌어 두 팔 모두 새로 생성한 답 있는 문항의 판정 정확도 합 후보 ≥ 기준 − JUDGE_TOLERANCE
# - F4: 생성한 한국어 문항(답 있는·없는 모두)의 섞인 답 수 후보 ≤ 기준
def test_command(
    floors: dict[str, float],
    base_na: dict,
    cand_na: dict,
    base_ans: dict,
    cand_ans: dict,
    used_retrieval: list[dict],
    c_adopted: bool,
) -> dict:
    cand_na_merged = merge_candidate(base_na, cand_na)
    refusals_base = sum(refused(r) for r, _ in base_na.values())
    refusals_cand = sum(refused(r) for r, _ in cand_na_merged.values())
    lost = {
        lang: sum(floor_effect(r, f)["lost"] for r in used_retrieval if r["language"] == lang)
        for lang, f in floors.items()
    }

    def score(pair: tuple[dict, dict | None]) -> int:
        _, j = pair
        return (j or {}).get("correctness_score") or UNJUDGED_SCORE

    common = sorted(set(base_ans) & set(cand_ans))
    ans_base_sum = sum(score(base_ans[k]) for k in common)
    ans_cand_sum = sum(score(cand_ans[k]) for k in common)

    def kana(rows: dict) -> int:
        return sum(1 for r, _ in rows.values() if r["language"] == "ko" and r.get("kana_han"))

    conditions = {
        "F1_refusal_gain": refusals_cand >= refusals_base + MIN_REFUSAL_GAIN,
        "F2_gold_lost": all(n <= MAX_LOST for n in lost.values()),
        "F3_answer_quality": ans_cand_sum >= ans_base_sum - JUDGE_TOLERANCE,
        "F4_mixed": kana(cand_na_merged) + kana(cand_ans) <= kana(base_na) + kana(base_ans),
    }
    # (c)의 효과(보고): 거절인데 인용이 붙은 답 수. (c)를 켜면 후보 팔의 거절 답 인용을 비운다(답 글은 같음).
    with_cites_base = sum(1 for r, _ in base_na.values() if refused(r) and r.get("cited_chunk_numbers"))
    with_cites_cand = (
        0
        if c_adopted
        else sum(1 for r, _ in cand_na_merged.values() if refused(r) and r.get("cited_chunk_numbers"))
    )
    hallucinated = {
        "base": sum(1 for _, j in base_na.values() if j and j.get("hallucinated")),
        "cand": sum(1 for _, j in cand_na_merged.values() if j and j.get("hallucinated")),
    }
    return {
        "floors": floors,
        "unanswerable_n": len(base_na),
        "refusals": {"base": refusals_base, "cand": refusals_cand},
        "refusals_by_language": {
            lang: {
                "base": sum(refused(r) for r, _ in base_na.values() if r["language"] == lang),
                "cand": sum(refused(r) for r, _ in cand_na_merged.values() if r["language"] == lang),
                "n": sum(1 for r, _ in base_na.values() if r["language"] == lang),
            }
            for lang in sorted({r["language"] for r, _ in base_na.values()})
        },
        "regenerated_unanswerable": sorted(k[1] for k in cand_na),
        "gold_lost_used_sets": lost,
        "answerable_changed": len(common),
        "answerable_correctness": {"base": ans_base_sum, "cand": ans_cand_sum},
        "refusals_with_citations": {"base": with_cites_base, "cand": with_cites_cand},
        "hallucinated_unanswerable": hallucinated,
        "conditions": conditions,
        "adopt_floor_and_refusal": bool(floors) and all(conditions.values()),
        "adopt_empty_citations": c_adopted,
    }


def _render(title: str, data: dict) -> str:
    import json

    return f"# {title}\n\n```json\n{json.dumps(data, ensure_ascii=False, indent=2)}\n```\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="v15 I4 답 없는 질문의 거절과 언어별 바닥값")
    sub = parser.add_subparsers(dest="command", required=True)
    fp = sub.add_parser("floors", help="dev 검색 기록(바닥값 0)에서 언어별 바닥값 후보를 고른다")
    fp.add_argument("--tag", required=True)
    fp.add_argument("--answerable", type=Path, nargs="+", required=True)
    fp.add_argument("--unanswerable", type=Path, nargs="+", required=True)
    cp = sub.add_parser("changed", help="고른 바닥값으로 문맥이 바뀌는 문항 id를 쓴다")
    cp.add_argument("--floors", type=Path, required=True)
    cp.add_argument("--out", type=Path, required=True)
    cp.add_argument("retrieval", type=Path, nargs="+")
    dp = sub.add_parser("dev", help="(c) 거절 답의 인용 비우기 조건")
    dp.add_argument("--tag", required=True)
    dp.add_argument("--label", required=True)
    dp.add_argument("--answerable", type=Path, nargs="+", required=True)
    dp.add_argument("--unanswerable", type=Path, nargs="+", required=True)
    tp = sub.add_parser("test", help="test 한 번: 기준과 후보를 비교해 채택 여부를 낸다")
    tp.add_argument("--tag", required=True)
    tp.add_argument("--label", required=True)
    tp.add_argument("--floors", type=Path, required=True)
    tp.add_argument("--base-na", type=Path, nargs="+", required=True)
    tp.add_argument("--cand-na", type=Path, nargs="*", default=[])
    tp.add_argument("--base-ans", type=Path, nargs="*", default=[])
    tp.add_argument("--cand-ans", type=Path, nargs="*", default=[])
    tp.add_argument("--used-retrieval", type=Path, nargs="+", required=True)
    tp.add_argument("--c-adopted", type=lambda v: v.lower() == "true", required=True)
    args = parser.parse_args()
    stamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")

    if args.command == "floors":
        answerable = [r for p in args.answerable for r in read_jsonl(p)]
        unanswerable = [r for p in args.unanswerable for r in read_jsonl(p)]
        result = floors_command(answerable, unanswerable)
        write_json(Path("eval/runs") / f"{args.tag}.json", result)
        write_report(f"refusal_floors_{args.tag}_{stamp}.md", _render(f"바닥값 후보 {args.tag}", result))
        print(f"candidate floors: {result['candidate_floors']}")
        return 0
    if args.command == "changed":
        floors = read_json(args.floors)["candidate_floors"]
        ids = [i for p in args.retrieval for i in changed_ids(read_jsonl(p), floors)]
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text("".join(f"{i}\n" for i in ids), encoding="utf-8")
        print(f"{len(ids)} items change context -> {args.out}")
        return 0
    if args.command == "dev":
        result = dev_command(
            load_answers(args.answerable, args.label), load_answers(args.unanswerable, args.label)
        )
        write_json(Path("eval/runs") / f"{args.tag}.json", result)
        write_report(f"refusal_dev_{args.tag}_{stamp}.md", _render(f"거절 dev {args.tag}", result))
        print(f"(c) adopted for test: {result['c_adopted_for_test']}")
        return 0

    floors = read_json(args.floors)["candidate_floors"]
    result = test_command(
        floors,
        load_answers(args.base_na, args.label),
        load_answers(args.cand_na, args.label),
        load_answers(args.base_ans, args.label),
        load_answers(args.cand_ans, args.label),
        [r for p in args.used_retrieval for r in read_jsonl(p)],
        args.c_adopted,
    )
    write_json(Path("eval/runs") / f"{args.tag}.json", result)
    write_report(f"refusal_test_{args.tag}_{stamp}.md", _render(f"거절 test {args.tag}", result))
    print(f"adopt floor+refusal: {result['adopt_floor_and_refusal']}, conditions {result['conditions']}")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(errors="backslashreplace")
    sys.exit(main())

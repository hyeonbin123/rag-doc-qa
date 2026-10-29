"""답 없는 질문의 거절과 언어별 바닥값(docs/experiments.md v15 I4).

사용법:
    # dev: 바닥값 0으로 돌린 검색 기록에서 언어별 바닥값 후보를 고른다(CPU)
    python -m eval.refusal floors --tag v15_i4_floors \
        --answerable <답 있는 dev 검색 기록 ...> --unanswerable <답 없는 dev 검색 기록 ...>

    # 고른 바닥값으로 문맥(상위 5개)이 바뀌는 문항을 '데이터셋<TAB>id' 줄로 쓴다(다시 생성할 문항.
    # eval/run_answer_eval.py --ids-file이 자기 데이터셋 줄만 읽는다)
    python -m eval.refusal changed --floors eval/runs/v15_i4_floors.json --out <ids.txt> \
        <retrieval.jsonl ...>

    # dev: 거절 답의 인용 비우기(c)를 고르는 조건
    python -m eval.refusal dev --tag v15_i4_dev --label J1 \
        --answerable <gen.jsonl ...> --unanswerable <gen.jsonl ...>

    # test: 기준(지금 기본값)과 후보(바닥값 + 청크 0개 거절)를 비교해 채택 여부를 낸다
    python -m eval.refusal test --tag v15_i4_test --label J1 --floors eval/runs/v15_i4_floors.json \
        --base-na <gen ...> --cand-na <gen ...> --base-ans <gen ...> --cand-ans <gen ...> \
        --used-retrieval <retrieval.jsonl ...> --c-adopted true|false

    # dev·test 모두 --by-kind를 더하면 거절 수를 질문 유형(near_miss/adjacent)별로도 보고한다(질문 풀 5)

    # v16-B(생성 쪽 거절 지시, docs/experiments.md v16-B): A(REFUSAL_STYLE=legacy)와 B(fixed)를 비교한다.
    # dev 관문(test를 열지 정함, test 기록 없이)
    python -m eval.refusal prompt-arms --tag v16b_dev --label J2v16b --report-label J1v16b \
        --a-ans <답 있는 dev gen ...> --b-ans <...> --a-na <답 없는 dev gen ...> --b-na <...>
    # test 결정(위와 같은 dev 기록 + 답 없는 test 기록)
    python -m eval.refusal prompt-arms --tag v16b_test ... --a-test <gen ...> --b-test <gen ...>
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
# [유형 열] --by-kind를 주면 dev·test 보고가 거절 수를 언어별 합계와 함께 질문 유형별로도 낸다
# (*_by_kind). 유형은 near_miss(문서가 주제는 다루지만 묻는 핵심이 없는 질문)와 adjacent(문서가 아예
# 다루지 않는 인접 주제)이고 문항 id로 정한다(question_kind). 질문 풀 5(eval/pool5_provenance.md)부터 두
# 유형이 한 셋에 섞여서, 합계만 보면 비교적 쉬운 인접 주제의 거절이 near-miss에서 지어낸 답을 가리기
# 때문이다. 기본은 끔: 커밋된 v15 I4 결정 기록(eval/runs/v15_i4_dev.json·v15_i4_test.json)은 이 열 없이
# 쓰였고, 같은 기록을 다시 세면 그 파일과 완전히 같아야 하기 때문이다(tests/test_v15_eval.py의 재집계).
# [v16-B] prompt-arms는 생성 쪽 거절 지시의 두 팔(A = 지금 프롬프트, B = 언어별 고정 거절문)을 측정 전에
# 등록한 규칙(docs/experiments.md v16-B)대로 비교한다. test 기록 없이 부르면 dev 관문(답 없는 test를 열지)을,
# test 기록과 함께 부르면 채택 여부를 낸다. 규칙의 문턱·셋·멈춤 조건은 아래 상수와 tests/test_v16_eval.py가
# 고정한다.

from __future__ import annotations

import argparse
import json
import math
import re
import statistics
import sys
from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from app.services.generation import FIXED_REFUSAL, is_refusal_answer
from app.services.retrieval import SCORE_FLOOR, page_key
from eval.common import (
    RUNS_DIR,
    dataset_sha256,
    format_ids_lines,
    git_commit,
    read_json,
    read_jsonl,
    write_json,
    write_report,
)
from eval.compare_judgments import paired_bootstrap_ci
from eval.judge import answer_sha1
from eval.run_judge import judged_path, meta_path

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


# 고른 바닥값으로 문맥이 바뀌는 문항(다시 생성할 문항)을 (데이터셋 이름, id) 짝으로 돌려준다. 후보 바닥값이
# 없는 언어의 문항은 바뀌지 않는다. 데이터셋 이름은 검색 기록의 dataset 필드(질문셋 파일 이름)다.
# 왜 짝인가: test3b 영어·한국어처럼 다른 셋이 같은 id를 쓰므로, id만 돌려주면 한 셋에서만 문맥이 바뀐 문항이
# 다른 셋에서도 다시 생성된다(v15 I4에서 8문항. 그 영향은 docs/experiments.md I4 test 결과에 적음). 문맥이
# 바뀐 기록에 dataset 이름이 없으면 어느 셋의 문항인지 알 수 없으므로 ValueError(eval/run_retrieval_eval.py로
# 다시 낸 기록에는 늘 있다).
def changed_ids(records: list[dict], floors: dict[str, float]) -> list[tuple[str, str]]:
    pairs = []
    for r in records:
        if r["language"] not in floors or not floor_effect(r, floors[r["language"]])["changed"]:
            continue
        if not r.get("dataset"):
            raise ValueError(
                f"retrieval record {r['id']!r} has no dataset name; rerun eval.run_retrieval_eval"
            )
        pairs.append((r["dataset"], r["id"]))
    return pairs


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


# 질문 유형을 정하는 문항 id 모양: 언어 글자(k/e) + 풀 번호 + 유형 글자 + 번호. 유형 글자 n은 near-miss
# (질문 풀 5의 k5n01·e5n01), a는 인접 주제(질문 풀 4의 k4a01·e4a01, 질문 풀 5의 k5a01·e5a01)다.
_KIND_ID = re.compile(r"[ke]\d+(?P<letter>[na])\d+")


# 문항 id → 질문 유형('near_miss' / 'adjacent'). 위 모양이 아닌 id(질문 풀 4 본 파일의 k4001, 이전 셋의
# id 등)는 'other'로 둔다. 생성 기록에는 유형 필드가 없고(질문셋 형식 eval/common.EvalQuestion에도 없음)
# 질문을 쓸 때 정한 id가 그 유형을 담고 있어서, 기록 형식을 바꾸지 않고 id로 가른다. 유형은 질문을 쓴 쪽의
# 의도이고, 답이 있는지는 라벨(셋의 종류)이 정한다.
def question_kind(item_id: str) -> str:
    match = _KIND_ID.fullmatch(item_id)
    if match is None:
        return "other"
    return "near_miss" if match["letter"] == "n" else "adjacent"


# 생성 기록들의 유형별 문항 수와 거절 수({유형: {"n": 문항 수, "refusals": 거절 수}}, 유형 이름순).
def kind_breakdown(records: Iterable[dict]) -> dict[str, dict[str, int]]:
    counts: dict[str, dict[str, int]] = {}
    for r in records:
        entry = counts.setdefault(question_kind(r["id"]), {"n": 0, "refusals": 0})
        entry["n"] += 1
        entry["refusals"] += int(refused(r))
    return dict(sorted(counts.items()))


# dev 명령: (c) 거절 답의 인용 비우기를 고르는 조건. 답 있는 dev 답 중 '판정 정확도 ≥ 4인데 거절로 분류된'
# 답이 언어별 MAX_FALSE_REFUSALS 이하이면 (c)를 test 후보에 넣는다. 답 없는 dev 질문의 거절 수와 거절인데
# 인용이 붙은 답 수는 보고한다. by_kind이면 답 있는·없는 질문의 거절 수를 유형별로도 보고한다
# (answerable_by_kind, unanswerable_by_kind. 답 있는 쪽은 거절 과잉을 유형별로 보려는 것).
def dev_command(answerable: dict, unanswerable: dict, by_kind: bool = False) -> dict:
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
        if by_kind:
            out["languages"][language]["answerable_by_kind"] = kind_breakdown(r for r, _ in ans)
            out["languages"][language]["unanswerable_by_kind"] = kind_breakdown(r for r, _ in na)
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
# 답 없는 질문의 거절 수는 언어별(refusals_by_language)로, by_kind이면 언어·유형별(refusals_by_kind)로도
# 보고한다. 유형 열은 보고용이고 F1~F4 판정에는 쓰지 않는다(v15 I4 규칙은 합계 기준).
def test_command(
    floors: dict[str, float],
    base_na: dict,
    cand_na: dict,
    base_ans: dict,
    cand_ans: dict,
    used_retrieval: list[dict],
    c_adopted: bool,
    by_kind: bool = False,
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
    result = {
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
    if by_kind:
        # 언어 → 유형 → 기준·후보 거절 수와 문항 수. 후보 쪽은 다시 생성하지 않은 문항에 기준 답을 쓴 병합
        # 결과(cand_na_merged, 키가 base_na와 같음)로 센다.
        kinds: dict[str, dict[str, dict[str, int]]] = {}
        for key, (r, _) in base_na.items():
            entry = kinds.setdefault(r["language"], {}).setdefault(
                question_kind(r["id"]), {"base": 0, "cand": 0, "n": 0}
            )
            entry["n"] += 1
            entry["base"] += int(refused(r))
            entry["cand"] += int(refused(cand_na_merged[key][0]))
        result["refusals_by_kind"] = {
            lang: dict(sorted(per_kind.items())) for lang, per_kind in sorted(kinds.items())
        }
    return result


# --- v16-B: 생성 쪽 거절 지시 두 팔 (prompt-arms) ---
# 등록한 규칙(docs/experiments.md v16-B, 측정 전에 커밋)을 코드로 옮긴 것이다.
# 팔 A = REFUSAL_STYLE=legacy(지금), B = fixed(언어별 1인칭 고정 거절문 + 한국어 규칙의 거절 문장). 나머지
# 생성 조건은 두 팔이 같아야 하고(아래 멈춤 조건), 거절은 생성 기록의 refusal 필드가 아니라 지금
# 분류기(refused)로 다시 센다.

# 등록한 셋: 파일 이름 → (문항 수, 언어). 답 있는 dev 7개(193문항), 답 없는 dev 4개(40), 답 없는 test 2개(94).
# 문항 id는 13개 셋 전체에서 겹치지 않아 보고의 문항 목록을 id만으로 적는다(tests/test_v16_eval.py가 확인).
SET_SIZES: dict[str, tuple[int, str]] = {
    "qa_dev.jsonl": (32, "en"),
    "qa_pool4_dev_en.jsonl": (40, "en"),
    "qa_pool5_ans_dev_en.jsonl": (3, "en"),
    "qa_dev_ko.jsonl": (32, "ko"),
    "qa_dev2_ko.jsonl": (40, "ko"),
    "qa_pool4_dev_ko.jsonl": (40, "ko"),
    "qa_pool5_ans_dev_ko.jsonl": (6, "ko"),
    "qa_pool4_na_dev_en.jsonl": (10, "en"),
    "qa_pool5_na_dev_en.jsonl": (10, "en"),
    "qa_pool4_na_dev_ko.jsonl": (10, "ko"),
    "qa_pool5_na_dev_ko.jsonl": (10, "ko"),
    "qa_pool5_na_test_en.jsonl": (52, "en"),
    "qa_pool5_na_test_ko.jsonl": (42, "ko"),
}
ANS_DEV_SETS = frozenset(n for n in SET_SIZES if "_na_" not in n)
NA_DEV_SETS = frozenset(n for n in SET_SIZES if "_na_dev_" in n)
TEST_SETS = frozenset(n for n in SET_SIZES if "_na_test_" in n)
# 조건 3(정확도 합)에 넣는 답 있는 dev 184문항(영어 72, 한국어 112). 질문 풀 5의 답 있는 near-miss(한국어 6,
# 영어 3)는 거절 과잉(조건 2)과 생성 시간(조건 6)에만 넣는다(정확도 합에서는 보고만).
ACCURACY_SETS = frozenset(
    {"qa_dev.jsonl", "qa_pool4_dev_en.jsonl", "qa_dev_ko.jsonl", "qa_dev2_ko.jsonl", "qa_pool4_dev_ko.jsonl"}
)
LANGUAGES = ("en", "ko")
# 조건 1: 답 없는 test의 거절 수 B − A 하한. 계획의 '30문항 기준'(한국어 +5, 영어 −1)을 실제 test 크기(한국어
# 42, 영어 52)에 같은 비율로 맞춰 올림한 값(5 × 42/30 = 7.0 → 7, −1 × 52/30 = −1.73 → −1)이다. 거절 수가
# 정수라 영어는 비율로 맞춰도 −1 그대로다. 측정 전에 정한 값이라 test 크기가 다르면 결정하지 않는다(멈춤).
MIN_TEST_GAIN = {"ko": 7, "en": -1}
MAX_EXTRA_FALSE_REFUSALS = 1  # 조건 2: '판정 ≥ 4인데 거절' B ≤ A + 1 (v15 I4 (c)와 같은 크기)
MAX_EXTRA_REFUSALS = 2  # 조건 2: 답 있는 dev에서 거절로 분류된 답 B ≤ A + 2
ACCURACY_TOLERANCE = 2  # 조건 3: 언어별 정확도 합 B ≥ A − 2 (v14·v15 I3와 같은 폭)
BOUNDARY_WIDTH = 1  # 판정 절차 규칙(v16부터)의 경계 규칙: 1회 판정 값이 한계와 1점 안이면 두 번 더 판정
MAX_EXTRA_P50_MS = 500.0  # 조건 6: 답 있는 dev 생성 시간 중앙값 B ≤ A + 0.5초
# 등록한 '나머지는 지금 기본값'(두 팔 모두). 생성 meta(eval/run_answer_eval.py)의 값과 같아야 한다.
REGISTERED_META: dict = {
    "provider": "ollama",
    "model": "a.x-4.0-light:q4_k_m",
    "database": "ragdb",
    "top_k": 5,
    "retrieval_mode": "dense",
    "cross_lingual": False,
    "score_floor": 0.3,
    "ids_file": None,
    "order": "dataset",
    "think": None,
    "language_guard": True,
    "citation_mode": "separate",
    "refuse_without_context": False,
    "empty_citations_on_refusal": True,
}
# 같은 셋의 A·B 실행이 같아야 하는 meta 키(거절 지시 꼴 refusal_style만 팔마다 다름). 같은 세션에서 A → B로
# 돌리므로 코드 커밋도 같아야 한다.
SAME_META_KEYS = (
    *REGISTERED_META,
    "model_digest",
    "embedding_models",
    "dataset_sha256",
    "corpus",
    "ollama_version",
    "git_commit",
)
# 한 단계(dev와 test)의 모든 실행이 같아야 하는 키: 본 DB 상태(코퍼스 요약)와 모델. 사이에 다시 적재했거나
# 모델을 바꿨으면 dev와 test가 다른 시스템을 잰 것이다.
STAGE_META_KEYS = ("database", "corpus", "embedding_models", "model_digest", "ollama_version")
# 판정 → 종료 코드(명령행). 0 test 열기·채택, 2 관문 탈락·채택 안 함, 3 멈춤(결정 안 함), 4 경계 규칙 필요.
VERDICT_EXIT = {"open_test": 0, "adopt": 0, "gate_failed": 2, "reject": 2, "stop": 3, "boundary": 4}

# 시스템 프롬프트의 2인칭 지시('say you don't know')를 그대로 베낀 영어 답의 첫머리(조건 5). 둥근 따옴표도
# 받는다.
_YOU_DONT_KNOW_RE = re.compile(r"you (?:do not|don't|don’t) know", re.IGNORECASE)


# 답이 (앞 공백을 떼고) "You don't know"로 시작하는지. "If you don't know …"처럼 중간에 있는 것은 세지 않는다.
def starts_with_you_dont_know(answer: str) -> bool:
    return bool(_YOU_DONT_KNOW_RE.match(answer.lstrip()))


# 고정 거절문을 어떻게 썼는지(보고용): exact(앞뒤 공백을 뗀 답이 그 언어의 고정 문장과 같음), prefix(고정
# 문장으로 시작하고 뒤에 더 씀), other_language(다른 언어의 고정 문장을 씀. 한국어 질문에 영어 문장을 쓰면
# 한국어 분류기가 거절로 세지 않음), none(그 밖).
def fixed_sentence_use(answer: str, language: str) -> str:
    text = answer.strip()
    own = FIXED_REFUSAL["ko" if language == "ko" else "en"]
    other = FIXED_REFUSAL["en" if language == "ko" else "ko"]
    if text == own:
        return "exact"
    if text.startswith(own):
        return "prefix"
    if other in text:
        return "other_language"
    return "none"


# 한 팔의 생성 기록. 각 묶음은 (데이터셋 파일 이름, 문항 id) → (생성 기록, 결정 판정 또는 None).
# ans: 답 있는 dev(결정 판정이 있어야 함), na: 답 없는 dev, test: 답 없는 test(dev 관문에서는 비어 있음),
# report: 답 있는 dev의 보고용 판정(J1), metas: 데이터셋 파일 이름 → 생성 meta, files: 읽은 파일(출처 기록용).
@dataclass
class PromptArm:
    ans: dict = field(default_factory=dict)
    na: dict = field(default_factory=dict)
    test: dict = field(default_factory=dict)
    report: dict = field(default_factory=dict)
    metas: dict = field(default_factory=dict)
    files: list = field(default_factory=list)


# 생성 기록 파일들과 그 옆의 meta(<기록>.meta.json), 판정(<기록>.<라벨>.judge.jsonl)을 읽어 한 팔을 만든다.
# 같은 (데이터셋, id)가 두 번 나오면(같은 셋 파일을 두 번 넘김) ValueError.
def load_prompt_arm(
    ans: list[Path], na: list[Path], test: list[Path], label: str, report_label: str | None = None
) -> PromptArm:
    arm = PromptArm()
    for group, paths in (("ans", ans), ("na", na), ("test", test)):
        rows = getattr(arm, group)
        for gen in paths:
            arm.files.append(gen)
            judged, reported = {}, {}
            if judged_path(gen, label).exists():
                judged = {j["id"]: j for j in read_jsonl(judged_path(gen, label))}
                arm.files.append(judged_path(gen, label))
            if report_label and judged_path(gen, report_label).exists():
                reported = {j["id"]: j for j in read_jsonl(judged_path(gen, report_label))}
                arm.files.append(judged_path(gen, report_label))
            meta = read_json(meta_path(gen)) if meta_path(gen).exists() else {}
            if meta:
                arm.files.append(meta_path(gen))
            for record in read_jsonl(gen):
                key = (record["dataset"], record["id"])
                if key in rows:
                    raise ValueError(f"{gen.name}: {key} appears twice in one arm")
                rows[key] = (record, judged.get(record["id"]))
                if group == "ans":
                    arm.report[key] = reported.get(record["id"])
                arm.metas.setdefault(record["dataset"], meta)
    return arm


def _of(rows: dict, language: str) -> list[tuple[tuple[str, str], dict, dict | None]]:
    return [(key, r, j) for key, (r, j) in sorted(rows.items()) if r.get("language") == language]


def _score(judgment: dict | None) -> int | float:
    return (judgment or {}).get("correctness_score") or UNJUDGED_SCORE


def _p50(values: list) -> float | None:
    known = [v for v in values if v is not None]
    return statistics.median(known) if known else None


def _all_rows(arm: PromptArm, groups: tuple[str, ...] = ("ans", "na", "test")) -> dict:
    return {key: pair for group in groups for key, pair in getattr(arm, group).items()}


# 멈춤 조건 1: 두 팔의 문항이 같고, 같은 문항은 같은 언어·같은 검색 청크(chunk_id 순서까지)를 받았는지. 같은
# DB를 같은 질문으로 검색했으므로 달라지면 DB나 검색이 두 실행 사이에 바뀐 것이다(팔 차이에 검색 차이가 섞임).
def _item_problems(a: PromptArm, b: PromptArm) -> list[str]:
    problems = []
    for group in ("ans", "na", "test"):
        rows_a, rows_b = getattr(a, group), getattr(b, group)
        only_a = sorted(k[1] for k in set(rows_a) - set(rows_b))
        only_b = sorted(k[1] for k in set(rows_b) - set(rows_a))
        if only_a or only_b:
            problems.append(
                f"{group}: items differ between the arms (only A {only_a[:10]}, only B {only_b[:10]})"
            )
        differ = [
            key[1]
            for key in sorted(set(rows_a) & set(rows_b))
            if rows_a[key][0].get("language") != rows_b[key][0].get("language")
            or [c.get("chunk_id") for c in rows_a[key][0].get("chunks") or []]
            != [c.get("chunk_id") for c in rows_b[key][0].get("chunks") or []]
        ]
        if differ:
            problems.append(f"{group}: {len(differ)} items got other chunks or language in B: {differ[:10]}")
    return problems


# 멈춤 조건 2: 생성 meta. A는 legacy, B는 fixed이고, 같은 셋의 두 실행은 SAME_META_KEYS가 같고, 둘 다 등록한
# 기본값(REGISTERED_META)이며, 단계 안의 모든 실행이 같은 DB 상태·모델(STAGE_META_KEYS)이어야 한다.
def _meta_problems(a: PromptArm, b: PromptArm) -> list[str]:
    problems = []
    for name, arm in (("A", a), ("B", b)):
        for dataset in sorted({d for d, _ in _all_rows(arm)}):
            if not arm.metas.get(dataset):
                problems.append(f"{name} {dataset}: no generation meta")
    for dataset in sorted(set(a.metas) & set(b.metas)):
        ma, mb = a.metas[dataset], b.metas[dataset]
        if not ma or not mb:
            continue
        for name, meta, style in (("A", ma, "legacy"), ("B", mb, "fixed")):
            if meta.get("refusal_style") != style:
                problems.append(
                    f"{name} {dataset}: refusal_style {meta.get('refusal_style')!r}, expected {style!r}"
                )
            for key, value in REGISTERED_META.items():
                if meta.get(key) != value:
                    problems.append(f"{name} {dataset}: {key} is {meta.get(key)!r}, registered {value!r}")
        problems += [
            f"{dataset}: {key} differs between the arms"
            for key in SAME_META_KEYS
            if ma.get(key) != mb.get(key)
        ]
    metas = [meta for arm in (a, b) for meta in arm.metas.values() if meta]
    for key in STAGE_META_KEYS:
        if key == "embedding_models":
            # 실행 meta의 embedding_models는 그 셋의 질문 언어만 담는다({"en": …} 또는 {"ko": …}).
            # 그래서 언어별로 모아, 같은 언어에 다른 모델(이름·리비전·자르기 차원)이 섞였을 때만 멈춘다.
            identities: dict[str, set] = {}
            for meta in metas:
                for language, identity in (meta.get(key) or {}).items():
                    identities.setdefault(language, set()).add(identity)
            differs = any(len(found) > 1 for found in identities.values())
        else:
            differs = (
                len({json.dumps(meta.get(key), sort_keys=True, ensure_ascii=False) for meta in metas}) > 1
            )
        if differs:
            problems.append(f"{key} differs between the runs of this stage")
    return problems


# 멈춤 조건 3: 답 있는 dev의 결정 판정. 두 팔의 모든 문항에 판정이 있고, 판정 오류·빈 점수·잘린 판정
# 프롬프트가 없고, 판정한 답(answer_sha1)이 이 기록의 답과 같아야 한다.
def _judge_problems(name: str, arm: PromptArm) -> list[str]:
    missing, errors, other_answer, truncated = [], [], [], []
    for key, (record, judgment) in sorted(arm.ans.items()):
        if judgment is None:
            missing.append(key[1])
            continue
        if judgment.get("error") or judgment.get("correctness_score") is None:
            errors.append(key[1])
        if judgment.get("answer_sha1") != answer_sha1(record["answer"]):
            other_answer.append(key[1])
        if judgment.get("truncation") == "truncated":
            truncated.append(key[1])
    labels = (
        ("no decision judgment", missing),
        ("judge error or no score", errors),
        ("judgment of another answer", other_answer),
        ("truncated judge prompt", truncated),
    )
    return [f"{name}: {what} for {len(ids)} items: {ids[:10]}" for what, ids in labels if ids]


# 멈춤 조건 4(check_registered일 때): 셋 이름과 문항 수가 등록한 것과 같아야 한다.
def _registered_problems(name: str, arm: PromptArm, has_test: bool) -> list[str]:
    problems = []
    for group, expected in (
        ("ans", ANS_DEV_SETS),
        ("na", NA_DEV_SETS),
        ("test", TEST_SETS if has_test else frozenset()),
    ):
        counts = Counter(dataset for dataset, _ in getattr(arm, group))
        if set(counts) != expected:
            problems.append(
                f"{name} {group}: sets {sorted(counts)} differ from the registered {sorted(expected)}"
            )
        for dataset, n in sorted(counts.items()):
            if dataset in SET_SIZES and n != SET_SIZES[dataset][0]:
                problems.append(f"{name} {dataset}: {n} items, registered {SET_SIZES[dataset][0]}")
    return problems


# 조건 2·3을 한 판정 라벨로 센다(결정 라벨, 또는 보고용 라벨). rows: (데이터셋, id) → (기록, 판정).
def _judged_conditions(a_rows: dict, b_rows: dict) -> tuple[dict, dict]:
    false_refusals: dict = {}
    accuracy: dict = {}
    for language in LANGUAGES:

        def good_refused(rows: dict, lang: str = language) -> list[str]:
            return [
                key[1]
                for key, r, j in _of(rows, lang)
                if refused(r)
                and (j or {}).get("correctness_score") is not None
                and j["correctness_score"] >= GOOD_ANSWER_MIN
            ]

        fa, fb = good_refused(a_rows), good_refused(b_rows)
        false_refusals[language] = {"a": fa, "b": fb, "pass": len(fb) <= len(fa) + MAX_EXTRA_FALSE_REFUSALS}
        keys = [key for key, r, _ in _of(a_rows, language) if key[0] in ACCURACY_SETS and key in b_rows]
        sum_a = sum(_score(a_rows[k][1]) for k in keys)
        sum_b = sum(_score(b_rows[k][1]) for k in keys)
        diff = sum_b - sum_a
        accuracy[language] = {
            "a": sum_a,
            "b": sum_b,
            "diff": diff,
            "n": len(keys),
            "pass": diff >= -ACCURACY_TOLERANCE,
            "boundary": abs(diff + ACCURACY_TOLERANCE) <= BOUNDARY_WIDTH,
        }
        if keys:
            mean, low, high = paired_bootstrap_ci([_score(b_rows[k][1]) - _score(a_rows[k][1]) for k in keys])
            accuracy[language]["ci90_sum"] = [round(low * len(keys), 3), round(high * len(keys), 3)]
            accuracy[language]["ci90_mean"] = [round(mean, 4), round(low, 4), round(high, 4)]
    false_refusals["pass"] = all(false_refusals[lang]["pass"] for lang in LANGUAGES)
    accuracy["pass"] = all(accuracy[lang]["pass"] for lang in LANGUAGES)
    return false_refusals, accuracy


def _refusal_counts(a_rows: dict, b_rows: dict) -> dict:
    out = {}
    for language in LANGUAGES:
        ra, rb = _of(a_rows, language), _of(b_rows, language)
        out[language] = {
            "a": sum(refused(r) for _, r, _ in ra),
            "b": sum(refused(r) for _, r, _ in rb),
            "n": len(ra),
            "a_by_kind": kind_breakdown(r for _, r, _ in ra),
            "b_by_kind": kind_breakdown(r for _, r, _ in rb),
        }
    return out


# 보고만(결정에 쓰지 않음): 등록한 '보고' 항목. 언어·유형별 거절 수, 고정 거절문을 쓴 방식, 답 길이·생성 시간
# 중앙값, 비워진 인용 수, 출력 상한에서 잘린 답 수, 거절로 분류되지 않은 답 없는 답과 거절로 분류된 답 있는
# 답의 목록, 정확도 합(질문 풀 5의 답 있는 셋 포함), 보고용 판정 라벨의 조건 2·3.
def _prompt_arms_report(a: PromptArm, b: PromptArm, groups: tuple[str, ...]) -> dict:
    arms = {"a": a, "b": b}

    def per_group(fn) -> dict:
        return {
            name: {
                group: {lang: fn(_of(getattr(arm, group), lang)) for lang in LANGUAGES} for group in groups
            }
            for name, arm in arms.items()
        }

    report: dict = {
        "refusals": {group: _refusal_counts(getattr(a, group), getattr(b, group)) for group in groups},
        "fixed_sentence_use": {
            name: {
                lang: dict(
                    sorted(
                        Counter(
                            fixed_sentence_use(r["answer"], lang) for _, r, _ in _of(_all_rows(arm), lang)
                        ).items()
                    )
                )
                for lang in LANGUAGES
            }
            for name, arm in arms.items()
        },
        "answer_chars_p50": per_group(lambda rows: _p50([len(r["answer"]) for _, r, _ in rows])),
        "generation_p50_ms": per_group(lambda rows: _p50([r.get("generation_ms") for _, r, _ in rows])),
        "emptied_citations": {
            name: {
                g: sum(1 for r, _ in getattr(arm, g).values() if r.get("citation_skipped") == "refusal")
                for g in groups
            }
            for name, arm in arms.items()
        },
        "length_stops": {
            name: sum(
                1
                for r, _ in _all_rows(arm).values()
                if (((r.get("generation_calls") or {}).get("answer") or [{}])[-1] or {}).get("done_reason")
                == "length"
            )
            for name, arm in arms.items()
        },
        "unanswerable_not_refused": {
            name: [key[1] for key, (r, _) in sorted(_all_rows(arm, ("na", "test")).items()) if not refused(r)]
            for name, arm in arms.items()
        },
        "answerable_refused": {
            name: [key[1] for key, (r, _) in sorted(arm.ans.items()) if refused(r)]
            for name, arm in arms.items()
        },
        "accuracy_all_answerable": {
            lang: {
                "a": sum(_score(j) for _, _, j in _of(a.ans, lang)),
                "b": sum(_score(j) for _, _, j in _of(b.ans, lang)),
                "n": len(_of(a.ans, lang)),
            }
            for lang in LANGUAGES
        },
        "report_label": None,
    }
    if any(j is not None for j in a.report.values()) or any(j is not None for j in b.report.values()):
        a_rows = {key: (r, a.report.get(key)) for key, (r, _) in a.ans.items()}
        b_rows = {key: (r, b.report.get(key)) for key, (r, _) in b.ans.items()}
        false_refusals, accuracy = _judged_conditions(a_rows, b_rows)
        report["report_label"] = {
            "C2_false_refusals": false_refusals,
            "C3_accuracy": accuracy,
            "unjudged": {
                "a": sum(1 for j in a.report.values() if j is None),
                "b": sum(1 for j in b.report.values() if j is None),
            },
        }
    return report


# prompt-arms의 본체. test가 비어 있으면 dev 관문, 있으면 test 결정이다.
# - dev 관문(test를 열기 전): 계획의 관문(답 없는 dev의 한국어 거절 수 B > A)에, dev 기록만으로 이미
#   정해지는 채택 조건(2, 3, 6과 dev 답의 5)을 더한다. 그 조건이 dev에서 떨어지면 test 결과와 상관없이
#   채택될 수 없으므로, 한 번만 쓸 수 있는 답 없는 test 셋을 열지 않고 남긴다.
# - test 결정: 관문을 통과한 dev 결과 + 조건 1(답 없는 test 거절 수), 조건 4(모든 한국어 답의 섞인 답), 조건
#   5(모든 영어 답). 관문이 닫혀 있었는데 test 기록이 있으면 결정하지 않는다(멈춤).
# - 경계 규칙: judged_with="once"(1회 판정 라벨)이고 조건 3의 값이 한계(−2)와 1점 안(−3~−1)이면, 판정과 무관한
#   조건이 모두 통과할 때(=결과가 판정에 달렸을 때)만 결정하지 않고 'boundary'를 낸다. 그때는 판정 절차
#   규칙대로 두 번 더 판정한 중앙값 라벨로 judged_with="median"을 주어 다시 부른다(조건 2의 판정 부분도 그
#   라벨로 다시 셈).
# - check_registered: 셋 이름·문항 수를 등록한 것과 맞춰 본다(명령행 기본 켬. 끄면 결과에 그 사실이 남음).
def prompt_arms_command(
    a: PromptArm, b: PromptArm, *, judged_with: str = "once", check_registered: bool = True
) -> dict:
    if judged_with not in ("once", "median"):
        raise ValueError(f"judged_with must be 'once' or 'median', not {judged_with!r}")
    has_test = bool(a.test or b.test)
    groups = ("ans", "na", "test") if has_test else ("ans", "na")
    stop = _item_problems(a, b) + _meta_problems(a, b) + _judge_problems("A", a) + _judge_problems("B", b)
    if check_registered:
        stop += _registered_problems("A", a, has_test) + _registered_problems("B", b, has_test)

    ko_na = {
        "a": sum(refused(r) for _, r, _ in _of(a.na, "ko")),
        "b": sum(refused(r) for _, r, _ in _of(b.na, "ko")),
    }
    ko_na |= {"n": len(_of(a.na, "ko")), "pass": ko_na["b"] > ko_na["a"]}
    false_refusals, accuracy = _judged_conditions(a.ans, b.ans)
    refusals_ans = {}
    for language in LANGUAGES:
        ra = sum(refused(r) for _, r, _ in _of(a.ans, language))
        rb = sum(refused(r) for _, r, _ in _of(b.ans, language))
        refusals_ans[language] = {"a": ra, "b": rb, "pass": rb <= ra + MAX_EXTRA_REFUSALS}
    refusals_ans["pass"] = all(refusals_ans[lang]["pass"] for lang in LANGUAGES)
    p50_a = _p50([r.get("generation_ms") for r, _ in a.ans.values()])
    p50_b = _p50([r.get("generation_ms") for r, _ in b.ans.values()])
    p50 = {
        "a_ms": p50_a,
        "b_ms": p50_b,
        "pass": p50_a is not None and p50_b is not None and p50_b <= p50_a + MAX_EXTRA_P50_MS,
    }

    def you(arm: PromptArm, scope: tuple[str, ...]) -> list[str]:
        rows = _all_rows(arm, scope)
        return [
            key[1]
            for key, (r, _) in sorted(rows.items())
            if r.get("language") == "en" and starts_with_you_dont_know(r["answer"])
        ]

    def kana(arm: PromptArm) -> list[str]:
        rows = _all_rows(arm, groups)
        return [
            key[1] for key, (r, _) in sorted(rows.items()) if r.get("language") == "ko" and r.get("kana_han")
        ]

    scope = "dev+test" if has_test else "dev"
    you_a, you_b = you(a, groups), you(b, groups)
    kana_a, kana_b = kana(a), kana(b)
    conditions: dict = {
        "C1_test_refusals": None,
        "C2_false_refusals": false_refusals,
        "C2_refusals": refusals_ans,
        "C3_accuracy": accuracy,
        "C4_mixed": {"a": kana_a, "b": kana_b, "scope": scope, "pass": len(kana_b) <= len(kana_a)},
        "C5_you_dont_know": {"a": you_a, "b": you_b, "scope": scope, "pass": not you_b},
        "C6_generation_p50": p50,
    }
    parts = {
        "ko_unanswerable_dev_refusals": ko_na["pass"],
        "C2_false_refusals": false_refusals["pass"],
        "C2_refusals": refusals_ans["pass"],
        "C3_accuracy": accuracy["pass"],
        "C5_you_dont_know": not you(b, ("ans", "na")),
        "C6_generation_p50": p50["pass"],
    }
    dev_gate = {"ko_unanswerable_dev_refusals": ko_na, "parts": parts, "open_test": all(parts.values())}
    # 판정 점수와 무관한 조건: 이것이 하나라도 떨어지면 판정을 더 해도 결과가 같다.
    judge_free = [
        parts[k]
        for k in ("ko_unanswerable_dev_refusals", "C2_refusals", "C5_you_dont_know", "C6_generation_p50")
    ]
    final_parts = None
    if has_test:
        c1: dict = {}
        for language in LANGUAGES:
            ra = sum(refused(r) for _, r, _ in _of(a.test, language))
            rb = sum(refused(r) for _, r, _ in _of(b.test, language))
            c1[language] = {
                "a": ra,
                "b": rb,
                "n": len(_of(a.test, language)),
                "min_gain": MIN_TEST_GAIN[language],
                "pass": rb - ra >= MIN_TEST_GAIN[language],
            }
        c1["pass"] = all(c1[lang]["pass"] for lang in LANGUAGES)
        conditions["C1_test_refusals"] = c1
        final_parts = {
            "dev_gate": dev_gate["open_test"],
            "C1_test_refusals": c1["pass"],
            "C4_mixed": conditions["C4_mixed"]["pass"],
            "C5_you_dont_know": conditions["C5_you_dont_know"]["pass"],
        }
        judge_free += [
            final_parts["C1_test_refusals"],
            final_parts["C4_mixed"],
            final_parts["C5_you_dont_know"],
        ]
    boundary_rule_needed = (
        judged_with == "once" and any(accuracy[lang]["boundary"] for lang in LANGUAGES) and all(judge_free)
    )

    adopt = None
    if stop:
        verdict = "stop"
    elif boundary_rule_needed:
        verdict = "boundary"
    elif not has_test:
        verdict = "open_test" if dev_gate["open_test"] else "gate_failed"
    elif not dev_gate["open_test"]:
        stop.append(
            "the dev gate did not pass with these dev records; the test set should not have been opened"
        )
        verdict = "stop"
    else:
        adopt = all(final_parts.values())
        verdict = "adopt" if adopt else "reject"
    return {
        "mode": "test" if has_test else "dev",
        "judged_with": judged_with,
        "registered_check": check_registered,
        "verdict": verdict,
        "stop": stop,
        "boundary_rule_needed": boundary_rule_needed,
        "dev_gate": dev_gate,
        "final_parts": final_parts,
        "adopt": adopt,
        "conditions": conditions,
        "report": _prompt_arms_report(a, b, groups),
    }


def _render(title: str, data: dict) -> str:
    return f"# {title}\n\n```json\n{json.dumps(data, ensure_ascii=False, indent=2)}\n```\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "답 없는 질문의 거절: v15 I4 언어별 바닥값(floors·changed·dev·test), "
            "v16-B 거절 지시 두 팔(prompt-arms)"
        )
    )
    sub = parser.add_subparsers(dest="command", required=True)
    fp = sub.add_parser("floors", help="dev 검색 기록(바닥값 0)에서 언어별 바닥값 후보를 고른다")
    fp.add_argument("--tag", required=True)
    fp.add_argument("--answerable", type=Path, nargs="+", required=True)
    fp.add_argument("--unanswerable", type=Path, nargs="+", required=True)
    cp = sub.add_parser(
        "changed",
        help="고른 바닥값으로 문맥이 바뀌는 문항을 '데이터셋<TAB>id' 줄로 쓴다(run_answer_eval --ids-file용)",
    )
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
    # 유형 열(near_miss / adjacent / other별 거절 수). 끄면 v15 I4 결정 기록과 같은 모양의 보고가 나온다.
    by_kind_help = (
        "거절 수를 질문 유형(near_miss/adjacent/other, 문항 id로 정함)별로도 보고한다. 두 유형이 섞인 "
        "질문 풀 5 셋에 쓴다. 기본은 끔(v15 I4 결정 기록이 이 열 없이 쓰였음)"
    )
    dp.add_argument("--by-kind", action="store_true", help=by_kind_help)
    tp.add_argument("--by-kind", action="store_true", help=by_kind_help)
    # v16-B prompt-arms: 팔 A(REFUSAL_STYLE=legacy)·B(fixed)의 생성 기록. 결과는 <RUNS_DIR>/<태그>.json과
    # eval/reports/refusal_prompt_arms_<태그>_<시각>.md이고, 종료 코드가 판정이다(VERDICT_EXIT).
    pp = sub.add_parser(
        "prompt-arms",
        help="v16-B 거절 지시 두 팔(A legacy, B fixed): test 기록 없이 dev 관문, 있으면 test 결정",
        description=(
            "docs/experiments.md v16-B에 측정 전에 등록한 규칙으로 두 팔을 비교한다. "
            "--a-test/--b-test가 없으면 dev 관문(답 없는 test를 열지), 있으면 채택 여부를 낸다. "
            "종료 코드: 0 test 열기·채택, 2 관문 탈락·채택 안 함, 3 멈춤(입력이 규칙과 어긋나 결정하지 "
            "않음), 4 경계 규칙 필요(두 번 더 판정한 중앙값 라벨로 --judged-with median을 주어 다시 부름)"
        ),
    )
    pp.add_argument("--tag", required=True, help="결과 파일 이름(<RUNS_DIR>/<태그>.json)")
    pp.add_argument(
        "--label",
        required=True,
        help="결정 판정 라벨(1회 판정 J2v16b, 경계 규칙을 썼으면 그 중앙값 라벨). 답 있는 dev 기록마다 "
        "<기록>.<라벨>.judge.jsonl이 있어야 한다",
    )
    pp.add_argument("--report-label", default=None, help="보고용 판정 라벨(예: J1v16b). 결정에 쓰지 않는다")
    pp.add_argument(
        "--judged-with",
        choices=["once", "median"],
        default="once",
        help="--label이 1회 판정이면 once(기본, 조건 3이 경계 안이면 결정하지 않고 종료 코드 4), 경계 규칙의 "
        "중앙값이면 median",
    )
    for arm in ("a", "b"):
        pp.add_argument(
            f"--{arm}-ans",
            type=Path,
            nargs="+",
            required=True,
            help=f"팔 {arm.upper()}의 답 있는 dev 생성 기록",
        )
        pp.add_argument(
            f"--{arm}-na",
            type=Path,
            nargs="+",
            required=True,
            help=f"팔 {arm.upper()}의 답 없는 dev 생성 기록",
        )
        pp.add_argument(
            f"--{arm}-test",
            type=Path,
            nargs="*",
            default=[],
            help=f"팔 {arm.upper()}의 답 없는 test 생성 기록(결정 때만)",
        )
    pp.add_argument(
        "--no-registered-check",
        action="store_true",
        help="셋 이름·문항 수를 등록한 v16-B 셋과 맞춰 보지 않는다(다른 셋에 도구를 쓸 때·테스트용). "
        "결정 실행에는 쓰지 않으며, 쓰면 결과의 registered_check가 false로 남는다",
    )
    args = parser.parse_args()
    stamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")

    if args.command == "prompt-arms":
        a = load_prompt_arm(args.a_ans, args.a_na, args.a_test, args.label, args.report_label)
        b = load_prompt_arm(args.b_ans, args.b_na, args.b_test, args.label, args.report_label)
        result = prompt_arms_command(
            a, b, judged_with=args.judged_with, check_registered=not args.no_registered_check
        )
        # 출처: 이 결과를 낸 코드 커밋과 읽은 파일(이름과 LF로 맞춘 sha256). 로컬 절대 경로는 남기지 않는다.
        result = {
            "tag": args.tag,
            "label": args.label,
            "report_label": args.report_label,
            **result,
            "provenance": {
                "git_commit": git_commit(),
                "files": {path.name: dataset_sha256(path) for path in [*a.files, *b.files]},
            },
        }
        write_json(RUNS_DIR / f"{args.tag}.json", result)
        title = f"v16-B 거절 지시 두 팔 {args.tag}: {result['verdict']}"
        write_report(f"refusal_prompt_arms_{args.tag}_{stamp}.md", _render(title, result))
        print(f"verdict: {result['verdict']}")
        for problem in result["stop"]:
            print(f"stop: {problem}")
        if result["boundary_rule_needed"]:
            print(
                "condition 3 is within 1 point of its limit: run the boundary rule, then --judged-with median"
            )
        return VERDICT_EXIT[result["verdict"]]

    if args.command == "floors":
        answerable = [r for p in args.answerable for r in read_jsonl(p)]
        unanswerable = [r for p in args.unanswerable for r in read_jsonl(p)]
        result = floors_command(answerable, unanswerable)
        write_json(Path("eval/runs") / f"{args.tag}.json", result)
        write_report(f"refusal_floors_{args.tag}_{stamp}.md", _render(f"바닥값 후보 {args.tag}", result))
        print(f"candidate floors: {result['candidate_floors']}")
        return 0
    if args.command == "changed":
        # 줄 끝을 LF로 고정해(newline="\n") Windows에서 써도 커밋된 다른 기록처럼 같은 바이트가 된다.
        floors = read_json(args.floors)["candidate_floors"]
        pairs = [pair for p in args.retrieval for pair in changed_ids(read_jsonl(p), floors)]
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(format_ids_lines(pairs), encoding="utf-8", newline="\n")
        print(f"{len(pairs)} items change context -> {args.out}")
        return 0
    if args.command == "dev":
        result = dev_command(
            load_answers(args.answerable, args.label),
            load_answers(args.unanswerable, args.label),
            by_kind=args.by_kind,
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
        by_kind=args.by_kind,
    )
    write_json(Path("eval/runs") / f"{args.tag}.json", result)
    write_report(f"refusal_test_{args.tag}_{stamp}.md", _render(f"거절 test {args.tag}", result))
    print(f"adopt floor+refusal: {result['adopt_floor_and_refusal']}, conditions {result['conditions']}")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(errors="backslashreplace")
    sys.exit(main())

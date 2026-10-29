"""v15 평가 도구(판정 흔들림 진단, 인용 호출 비교, 거절·바닥값, 판정 패널)를 가짜 기록으로 검증한다.

docs/experiments.md v15의 결정 규칙이 코드와 같은지 고정한다. DB·Ollama 없이 돈다.
"""

# [테스트 묶음] eval/judge_stability.py, eval/citation_arms.py, eval/refusal.py, eval/judge_panel.py의 순수
# 함수와, eval/judge.py에 더한 think·캐시 되돌리기 요청 본문. 두 판정기 평균 라벨(0.5점 단위)은
# eval/generator_arms.py summary와 eval/refusal.py가 그대로 합치는지도 본다.
# [왜 중요한가] 이 도구들은 측정 전에 등록한 규칙을 그대로 옮긴 것이다. 규칙과 다르게 세면 측정 뒤에 결정이
# 바뀌므로, 경계값(같음/다름, 허용 폭의 끝)을 가짜 기록으로 고정한다.

import json
import sys
from pathlib import Path

import pytest

from eval import citation_arms, generator_arms, judge_panel, judge_stability, refusal
from eval.common import format_ids_lines, read_ids_file, read_json, read_jsonl, write_jsonl
from eval.judge import (
    FLUSH_MESSAGES,
    JudgeConfig,
    answer_sha1,
    judge_items,
    ollama_flush_payload,
    ollama_judge_payload,
)
from eval.run_judge import judged_path

# --- eval/judge.py: think, 캐시 되돌리기 ---


# think를 주지 않으면 J1 요청 본문에 think 필드가 없다(전과 같은 요청). 주면 그 값이 들어간다.
def test_judge_payload_sends_think_only_when_set():
    assert "think" not in ollama_judge_payload("p", JudgeConfig(model="qwen2.5:7b-instruct"))
    payload = ollama_judge_payload("p", JudgeConfig(model="gemma4:12b-it-qat", think=False))
    assert payload["think"] is False


# 캐시 되돌리기 요청은 판정과 같은 모델·num_ctx·think로, 짧은 무관한 대화를 한 토큰만 생성한다.
def test_flush_payload_matches_the_judge_context_and_is_tiny():
    config = JudgeConfig(model="qwen2.5:7b-instruct", think=None)
    payload = ollama_flush_payload(config)
    assert payload["messages"] == FLUSH_MESSAGES
    assert payload["options"] == {"temperature": 0, "num_predict": 1, "num_ctx": 8192}
    assert "think" not in payload and "format" not in payload


# judge_items의 before_each는 판정할 문항마다 판정 직전에 한 번 불리고, 그 결과가 기록에 남는다. 청크가 없어
# 판정하지 않는 문항에서는 부르지 않는다.
@pytest.mark.asyncio
async def test_before_each_runs_once_per_judged_item():
    from eval.judge import JudgeOutcome

    calls = []

    async def fake_call(prompt):
        calls.append("judge")
        return JudgeOutcome(correctness_score=5, faithfulness_score=5, hallucinated=False, raw="{}")

    async def flush():
        calls.append("flush")
        return {"prompt_eval_count": 7}

    records = [
        {"id": "a", "question": "q", "answer": "x", "reference_answer": "r", "chunks": [{"content": "c"}]},
        {"id": "b", "question": "q", "answer": "x", "reference_answer": "r", "chunks": []},
    ]
    judgments = await judge_items(records, JudgeConfig(model="m"), fake_call, before_each=flush)
    assert calls == ["flush", "judge"]
    assert judgments[0]["flush"] == {"prompt_eval_count": 7}
    assert judgments[1]["flush"] is None


# --- eval/judge_stability.py ---


def _judgments(raws: dict[str, str], scores: dict[str, int] | None = None) -> dict:
    scores = scores or {}
    return {
        ("d", i): {
            "id": i,
            "raw": raw,
            "correctness_score": scores.get(i, 4),
            "faithfulness_score": 4,
            "hallucinated": False,
        }
        for i, raw in raws.items()
    }


# 원문이 다른 문항과 점수가 다른 문항을 따로 센다(원문만 다르고 점수가 같을 수 있다).
def test_pass_diff_counts_raw_and_score_differences():
    base = _judgments({"a": "x", "b": "y"})
    other = _judgments({"a": "x2", "b": "y"}, {"a": 4})
    diff = judge_stability.pass_diff(base, other)
    assert (diff["raw_diff"], diff["score_diff"]) == (1, 0)
    other = _judgments({"a": "x2", "b": "y"}, {"a": 5})
    assert judge_stability.pass_diff(base, other)["changed_ids"] == ["a"]


def _diffs(a2=0, r=0, f2=0, lr=0):
    return {name: {"raw_diff": v} for name, v in (("A2", a2), ("R", r), ("F1", 0), ("F2", f2), ("L", lr))}


# 등록한 결정표: (b) 같은 순서에서도 다름 → (c) 재현 안 됨 → (a) 캐시 되돌리기로 순서 효과가 사라짐 → (d)
# 아님.
@pytest.mark.parametrize(
    "diffs, outcome",
    [
        (_diffs(a2=1), "b"),
        (_diffs(a2=2, r=3, f2=0), "b"),
        (_diffs(), "c"),
        (_diffs(r=2), "a"),
        (_diffs(lr=1), "a"),
        (_diffs(r=2, f2=1), "d"),
    ],
)
def test_decide_follows_the_registered_table(diffs, outcome):
    assert judge_stability.decide(diffs)["outcome"] == outcome


# 중앙값 합치기: 정확도·충실도는 가운데 값, 환각은 다수결, 하나라도 빈 판정이면 빈 판정.
def test_median_judgments():
    def j(c, f, h, err=None):
        return {
            "id": "a",
            "dataset": "d",
            "correctness_score": c,
            "faithfulness_score": f,
            "hallucinated": h,
            "error": err,
            "judge_label": "x",
            "raw": "{}",
        }

    merged = judge_stability.median_judgments([[j(3, 5, True)], [j(5, 4, False)], [j(4, 4, True)]], "J1m3")
    assert (merged[0]["correctness_score"], merged[0]["faithfulness_score"], merged[0]["hallucinated"]) == (
        4,
        4,
        True,
    )
    assert merged[0]["judge_label"] == "J1m3"
    merged = judge_stability.median_judgments(
        [[j(3, 5, True)], [j(None, None, None, "HTTP 400")], [j(4, 4, True)]], "J1m3"
    )
    assert merged[0]["correctness_score"] is None


# 반복 판정 비교·평균 합치기 테스트용 판정 기록 하나. answer로 answer_sha1을 만들어, 같은 답을 판정했는지
# 가르는 확인이 실제 기록과 같은 필드로 돌게 한다.
def _judgment(
    item_id, raw="{}", c=4, f=4, h=False, answer="x", label="r", model="m", err=None, dataset="qa_dev.jsonl"
):
    return {
        "id": item_id,
        "dataset": dataset,
        "judge_label": label,
        "judge_model": model,
        "answer_sha1": answer_sha1(answer),
        "raw": raw,
        "correctness_score": c,
        "faithfulness_score": f,
        "hallucinated": h,
        "error": err,
        "truncation": "error" if err else "ok",
        "judge_ms": 2000.0,
    }


# repeats: 반복 판정 사이에 판정 원문이 다른 문항과 점수가 다른 문항을 따로 세고, 첫 판정이 문항별 중앙값과
# 다른 문항도 센다. 같은 (데이터셋, id)가 두 생성 기록(두 팔)에 있어도 한 문항으로 합치지 않는다. 다른 답을
# 판정한 기록은 반복으로 보지 않는다.
def test_repeats_counts_items_that_differ_between_repeated_judgments(tmp_path):
    gens = [tmp_path / "v16_c5_qa_dev.lg.gen.jsonl", tmp_path / "v16_c6_qa_dev.lg.gen.jsonl"]
    labels = ["r1", "r2", "r3"]

    def write(label, per_gen):
        for gen, records in zip(gens, per_gen, strict=True):
            write_jsonl(judged_path(gen, label), records)

    same = [[_judgment("d1"), _judgment("d2")], [_judgment("d1", answer="y"), _judgment("d2", answer="y")]]
    for label in labels:
        write(label, same)
    result = judge_stability.repeats(gens, labels)
    assert result["n"] == 4  # 두 팔의 d1·d2를 따로 셈
    assert (result["any_raw_diff"], result["any_score_diff"], result["first_differs_from_median"]) == (
        0,
        0,
        0,
    )

    # r3에서 c6 팔 d1의 원문만 다름(점수는 같음) → 원문 1, 점수 0
    write("r3", [same[0], [_judgment("d1", raw="{ }", answer="y"), _judgment("d2", answer="y")]])
    result = judge_stability.repeats(gens, labels)
    assert (result["any_raw_diff"], result["any_score_diff"]) == (1, 0)
    assert result["vs_first"]["r3"]["raw_diff"] == 1 and result["vs_first"]["r2"]["raw_diff"] == 0

    # r2에서 c5 팔 d2의 점수가 5 → 점수가 다른 문항 1. 중앙값(4, 5, 4 → 4)은 r1과 같음
    write("r2", [[_judgment("d1"), _judgment("d2", raw="{5}", c=5)], same[1]])
    result = judge_stability.repeats(gens, labels)
    assert result["any_score_diff"] == 1
    assert result["vs_first"]["r2"]["changed"] == ["v16_c5_qa_dev.lg.gen.jsonl#d2"]
    assert result["first_differs_from_median"] == 0

    # r3도 5점이면 중앙값(4, 5, 5 → 5)이 r1과 달라짐
    write("r3", [[_judgment("d1"), _judgment("d2", raw="{5}", c=5)], same[1]])
    result = judge_stability.repeats(gens, labels)
    assert result["first_differs_from_median"] == 1
    assert result["correctness_sum"] == {"r1": 16, "r2": 17, "r3": 17, "median": 17}

    write("r3", [[_judgment("d1", answer="z"), _judgment("d2")], same[1]])
    with pytest.raises(ValueError, match="different answer"):
        judge_stability.repeats(gens, labels)
    with pytest.raises(ValueError, match="two labels"):
        judge_stability.repeats(gens, ["r1"])


# average: 두 판정기의 문항별 평균. 정확도·충실도는 평균(0.5점 단위), 환각은 둘 중 하나라도 표시하면 표시, 한
# 판정이라도 오류·빈 판정이면 빈 판정(오류 문구는 남김). 다른 문항·다른 답을 판정한 기록은 합치지 않는다.
def test_average_judgments_means_the_scores_and_keeps_a_hallucination_flag_from_either_judge():
    j2 = [
        _judgment("a", c=4, f=5, h=False, label="J2", model="m2"),
        _judgment("b", c=3, f=3, label="J2", model="m2"),
        _judgment("c", label="J2", model="m2"),
    ]
    j3 = [
        _judgment("a", c=5, f=4, h=True, label="J3", model="m3"),
        _judgment("b", c=3, f=3, label="J3", model="m3"),
        _judgment("c", raw=None, c=None, f=None, h=None, label="J3", model="m3", err="HTTP 500"),
    ]
    merged = judge_stability.average_judgments([j2, j3], "J23")
    assert [(m["correctness_score"], m["faithfulness_score"], m["hallucinated"]) for m in merged] == [
        (4.5, 4.5, True),
        (3.0, 3.0, False),
        (None, None, None),
    ]
    first = merged[0]
    assert (first["judge_label"], first["merged_from"], first["judge_model"]) == (
        "J23",
        ["J2", "J3"],
        "m2+m3",
    )
    assert first["raw"] is None and first["judge_ms"] is None  # 한 번의 호출이 낸 값이 아님
    assert (merged[2]["error"], merged[2]["truncation"]) == ("HTTP 500", "error")
    with pytest.raises(ValueError, match="different answer"):
        judge_stability.average_judgments([j2, [_judgment("a", answer="other"), *j3[1:]]], "J23")
    with pytest.raises(ValueError, match="different items"):
        judge_stability.average_judgments([j2, j3[:2]], "J23")


# average 명령으로 만든 라벨(0.5점 단위)을 결정 도구가 그대로 읽어 합친다: generator_arms summary의 언어별
# 합과 기준 팔과의 차이(정수가 아닌 합의 표기 포함), eval.refusal dev의 '판정 4 이상' 문턱과 test의 F3 합.
def test_an_average_label_sums_in_half_points_through_generator_arms_and_refusal(tmp_path, monkeypatch):
    answers = {
        "a": {"d1": "I don't know.", "d2": "Use Query.", "d3": "Path를 쓰세요."},
        "b": {"d1": "Use Path.", "d2": "Use Query(alias=...).", "d3": "Path를 쓰면 됩니다."},
    }
    scores = {  # 판정기 → 팔 → 문항 → (정확도, 환각)
        "J2": {
            "a": {"d1": (4, False), "d2": (3, True), "d3": (5, False)},
            "b": {"d1": (5, False), "d2": (4, False), "d3": (5, False)},
        },
        "J3": {
            "a": {"d1": (5, False), "d2": (3, False), "d3": (4, False)},
            "b": {"d1": (5, False), "d2": (3, False), "d3": (5, False)},
        },
    }
    gens = {}
    for arm, by_id in answers.items():
        gens[arm] = tmp_path / f"v16_{arm}_qa_dev.lg.gen.jsonl"
        write_jsonl(
            gens[arm],
            [
                _gen_record(i, text, 1000.0, [1], language="ko" if i == "d3" else "en")
                for i, text in by_id.items()
            ],
        )
        for label, by_arm in scores.items():
            write_jsonl(
                judged_path(gens[arm], label),
                [
                    _judgment(i, c=c, f=c, h=h, answer=by_id[i], label=label, model=label)
                    for i, (c, h) in by_arm[arm].items()
                ],
            )
    argv = ["judge_stability", "average", "--labels", "J2", "J3", "--out-label", "J23"]
    monkeypatch.setattr(sys, "argv", [*argv, "--gen", str(gens["a"]), str(gens["b"])])
    assert judge_stability.main() == 0

    _, data = generator_arms.summary_report("t", "J23", {"A": [gens["a"]], "B": [gens["b"]]}, "A")
    a, b = (data["arms"][arm]["summary"] for arm in ("A", "B"))
    assert [a[lang]["correctness_sum"] for lang in ("en", "ko", "all")] == [7.5, 4.5, 12.0]
    assert (b["all"]["correctness_sum"], a["all"]["hallucinated"]) == (13.5, 1)
    vs = data["arms"]["B"]["vs_baseline"]
    assert [vs[lang].split()[0] for lang in ("en", "ko", "all")] == ["+1", "+0.5", "+1.5"]

    base, cand = (refusal.load_answers([gens[arm]], "J23") for arm in ("a", "b"))
    assert refusal.dev_command(base, {})["languages"]["en"]["false_refusals"] == ["d1"]  # 거절, 평균 4.5 ≥ 4
    result = refusal.test_command({}, {}, {}, base, cand, [], c_adopted=False)
    assert result["answerable_correctness"] == {"base": 12.0, "cand": 13.5}
    assert result["conditions"]["F3_answer_quality"] is True


# 커밋된 판정 기록이 있는 곳. 아래 두 테스트는 저장된 v15 판정만 읽으므로 DB·Ollama 없이 돈다.
V15_RUNS = Path(judge_stability.__file__).parent / "runs"


# 세 회 판정 묶음의 생성 기록들: <stem>.<판정 라벨>r1.judge.jsonl이 있는 <stem>.gen.jsonl.
def _v15_repeat_gens(label: str) -> list[Path]:
    suffix = f".{label}r1.judge.jsonl"
    return sorted(
        V15_RUNS / (p.name.removesuffix(suffix) + ".gen.jsonl") for p in V15_RUNS.glob(f"*{suffix}")
    )


# v15 I3~I5의 '같은 순서 3회 중앙값'은 1,847문항에서 아무것도 바꾸지 않았다(docs/experiments.md I2 결과의
# 2026-10-30 추가 분석): r1·r2·r3의 판정 원문이 모든 문항에서 같고, 결정에 쓴 중앙값 파일(J1v15·J2v15·J3v15)의
# 점수도 r1과 같다. 커밋된 repeats 결과 파일과도 같은지 본다. v16부터의 1회 판정 규칙의 근거를 저장된 기록으로
# 고정한다.
@pytest.mark.parametrize("label, files, n", [("J1v15", 38, 951), ("J2v15", 12, 448), ("J3v15", 12, 448)])
def test_the_v15_three_judgment_median_never_differed_from_the_first_judgment(label, files, n):
    gens = _v15_repeat_gens(label)
    assert len(gens) == files
    result = judge_stability.repeats(gens, [f"{label}r1", f"{label}r2", f"{label}r3"])
    assert result["n"] == n
    assert (result["any_raw_diff"], result["any_score_diff"], result["first_differs_from_median"]) == (
        0,
        0,
        0,
    )

    def scores(path: Path) -> dict:
        return {
            (j["dataset"], j["id"]): (j["correctness_score"], j["faithfulness_score"], j["hallucinated"])
            for j in read_jsonl(path)
        }

    for gen in gens:
        assert scores(judged_path(gen, label)) == scores(judged_path(gen, f"{label}r1")), gen.name
    committed = read_json(V15_RUNS / f"v15_{label}.repeats.json")
    assert {k: v for k, v in committed.items() if k not in ("tag", "date")} == result


# 경계 규칙의 폭(1점)의 근거: v15 I2에서 같은 dev 답 104문항을 이력만 바꿔 판정한 패스들(A1 기준, 곧바로
# 다시, 역순, 캐시 되돌리기 정순·역순, 다시 올린 뒤)의 언어별 정확도 합은 영어 32문항 152~153, 한국어 72문항
# 343~345로 A1(152, 344)에서 많아야 1점 움직였다(docs/experiments.md의 '규칙 변경 (v16부터): 판정 절차').
def test_the_v15_i2_passes_moved_each_language_sum_by_at_most_one_point():
    sums = {}
    for label in ("J1sA1", "J1sA2", "J1sR", "J1sF1", "J1sF2", "J1sL"):
        totals = {
            name: sum(
                j["correctness_score"] or 0
                for j in read_jsonl(V15_RUNS / f"v14_c3_{name}.lg.{label}.judge.jsonl")
            )
            for name in ("qa_dev", "qa_dev_ko", "qa_dev2_ko")
        }
        sums[label] = (totals["qa_dev"], totals["qa_dev_ko"] + totals["qa_dev2_ko"])
    assert sums["J1sA1"] == (152, 344)
    assert sorted({en for en, _ in sums.values()}) == [152, 153]
    assert sorted({ko for _, ko in sums.values()}) == [343, 344, 345]


# --- eval/citation_arms.py ---


def _gen_record(item_id, answer, ms, cited, language="en", expected="docs/en/docs/a.md", citation_ms=2000.0):
    return {
        "id": item_id,
        "dataset": "qa_dev.jsonl",
        "dataset_index": int(item_id[1:]),
        "language": language,
        "question": "q",
        "answer": answer,
        "reference_answer": "r",
        "expected_source_paths": [expected],
        "chunks": [
            {"source_path": "docs/en/docs/a.md", "content": "c", "chunk_id": "1"},
            {"source_path": "docs/en/docs/b.md", "content": "c", "chunk_id": "2"},
        ],
        "cited_chunk_numbers": cited,
        "generation_ms": ms,
        "kana_han": False,
        "citation_schema_error": None,
        "generation_calls": {"citation": {"ms": citation_ms, "prompt_eval_count": 100, "eval_count": 10}},
    }


def _write(tmp_path: Path, name: str, records: list[dict], judgments: dict[str, int] | None = None) -> Path:
    gen = tmp_path / f"{name}.gen.jsonl"
    gen.write_text("".join(json.dumps(r) + "\n" for r in records), encoding="utf-8")
    if judgments is not None:
        judged = tmp_path / f"{name}.J1.judge.jsonl"
        judged.write_text(
            "".join(
                json.dumps(
                    {
                        "id": r["id"],
                        "correctness_score": judgments[r["id"]],
                        "faithfulness_score": 4,
                        "hallucinated": False,
                        "answer_sha1": answer_sha1(r["answer"]),
                    }
                )
                + "\n"
                for r in records
            ),
            encoding="utf-8",
        )
    return gen


# 같은 답이면 A의 판정을 B에도 쓰고(B 자기 판정이 달라도), 1초 이상 빨라지고 인용이 유지되면 채택한다.
def test_citation_arms_shares_judgments_for_identical_answers_and_adopts(tmp_path):
    a = _write(
        tmp_path,
        "a",
        [_gen_record("d1", "same", 9000, [1]), _gen_record("d2", "same2", 9000, [1])],
        {"d1": 5, "d2": 5},
    )
    b = _write(
        tmp_path,
        "b",
        [_gen_record("d1", "same", 7500, [1]), _gen_record("d2", "same2", 7900, [1])],
        {"d1": 3, "d2": 3},
    )
    result = citation_arms.decide([a], [b], "J1")
    assert result["correctness_sum"] == {"A": 10, "B_shared": 10}
    assert result["adopt"] is True


# 1초에 못 미치게 빨라지거나, 빈 인용이 있거나, 인용 적중이 2문항 줄면 채택하지 않는다.
@pytest.mark.parametrize(
    "b_ms, b_cited, failing",
    [
        (8100, [1], "1_latency"),
        (7000, [], "3_schema"),
        (7000, [2], "2_citation_hits"),
    ],
)
def test_citation_arms_rejects(tmp_path, b_ms, b_cited, failing):
    a = _write(
        tmp_path,
        "a",
        [_gen_record("d1", "x", 9000, [1]), _gen_record("d2", "y", 9000, [1])],
        {"d1": 5, "d2": 5},
    )
    b = _write(
        tmp_path,
        "b",
        [_gen_record("d1", "x", b_ms, b_cited), _gen_record("d2", "y", b_ms, b_cited)],
        {"d1": 5, "d2": 5},
    )
    result = citation_arms.decide([a], [b], "J1")
    assert result["conditions"][failing] is False
    assert result["adopt"] is False


# --- eval/refusal.py ---


def _retrieval(item_id, scores, gold_ranks, language="ko"):
    return {
        "id": item_id,
        "language": language,
        "expected_source_paths": ["docs/ko/docs/gold.md"] if gold_ranks is not None else [],
        "results": [
            {
                "rank": i + 1,
                "score": s,
                "source_path": "docs/ko/docs/gold.md"
                if gold_ranks and i + 1 in gold_ranks
                else f"docs/ko/docs/x{i}.md",
            }
            for i, s in enumerate(scores)
        ],
    }


# 바닥값 f는 상위 5개 중 점수 ≥ f인 청크만 남긴다. 정답 손실은 상위 5개의 정답 청크가 모두 사라진 경우.
def test_floor_effect():
    r = _retrieval("a", [0.9, 0.85, 0.82, 0.81, 0.80, 0.79], gold_ranks={3})
    assert refusal.floor_effect(r, 0.3) == {"kept": 5, "changed": False, "zero": False, "lost": False}
    assert refusal.floor_effect(r, 0.83) == {"kept": 2, "changed": True, "zero": False, "lost": True}
    assert refusal.floor_effect(r, 0.95)["zero"] is True


# 고르는 바닥값 = (허용 손실 + 1)번째로 작은 정답 점수(셋째 자리 내림). 지금 0.3보다 낮으면 0.3.
def test_choose_floor_takes_the_second_smallest_gold_score():
    answerable = [
        _retrieval("a", [0.90, 0.80], gold_ranks={1}),
        _retrieval("b", [0.86, 0.84], gold_ranks={2}),
        _retrieval("c", [0.95, 0.94], gold_ranks={1}),
        _retrieval("d", [0.70, 0.60], gold_ranks=None),  # 정답이 상위 5개에 없음: 계산에서 빠짐
    ]
    assert refusal.choose_floor(answerable) == 0.9
    floor = refusal.choose_floor(answerable)
    assert sum(refusal.floor_effect(r, floor)["lost"] for r in answerable) == 1
    assert refusal.choose_floor([_retrieval("a", [0.2], gold_ranks={1}), _retrieval("b", [0.25], {1})]) == 0.3
    assert refusal.choose_floor([_retrieval("a", [0.9], gold_ranks={1})]) is None


# 답 없는 dev 질문 중 청크 0개가 되는 문항이 있을 때만 그 언어의 후보가 된다.
def test_floors_command_marks_a_language_effective_only_with_a_zero_chunk_unanswerable():
    answerable = [_retrieval("a", [0.90], {1}), _retrieval("b", [0.88], {1}), _retrieval("c", [0.95], {1})]
    unanswerable = [_retrieval("n1", [0.89, 0.85], None), _retrieval("n2", [0.91], None)]
    result = refusal.floors_command(answerable, unanswerable)
    assert result["languages"]["ko"]["chosen"] == 0.9
    assert result["candidate_floors"] == {"ko": 0.9}
    result = refusal.floors_command(answerable, [_retrieval("n2", [0.93], None)])
    assert result["candidate_floors"] == {}


# 다시 생성할 문항은 (데이터셋, id)로 고른다. test3b 영어·한국어 셋처럼 두 셋이 같은 id를 쓰면, 문맥이 바뀐
# 셋의 문항만 목록에 들어가야 한다. v15 I4에서는 id만 적은 목록을 썼기 때문에, 한쪽 셋에서만 문맥이 바뀐 id가
# 다른 셋에서도 두 팔로 다시 생성됐다. changed 명령은 '데이터셋<TAB>id' 줄을 쓰고, run_answer_eval의
# --ids-file 읽기(read_ids_file)는 자기 데이터셋 줄만 받는다. 데이터셋 이름이 없는 검색 기록으로는 목록을
# 만들지 않는다.
def test_changed_ids_name_the_dataset_so_a_shared_id_is_regenerated_only_where_its_context_changed(
    tmp_path, monkeypatch
):
    scores = [0.9, 0.85, 0.82, 0.81, 0.80]
    en = {**_retrieval("n010", scores, gold_ranks={1}, language="en"), "dataset": "qa_test3b_en.jsonl"}
    ko = {**_retrieval("n010", scores, gold_ranks={1}, language="ko"), "dataset": "qa_test3b_ko.jsonl"}
    floors = {"en": 0.5, "ko": 0.83}  # 영어는 다섯 개가 모두 남고(문맥 그대로), 한국어는 셋이 빠짐
    pairs = refusal.changed_ids([en, ko], floors)
    assert pairs == [("qa_test3b_ko.jsonl", "n010")]

    ids_file = tmp_path / "ids.txt"
    ids_file.write_text(format_ids_lines(pairs), encoding="utf-8")
    assert read_ids_file(ids_file, "qa_test3b_ko.jsonl") == {"n010"}
    assert read_ids_file(ids_file, "qa_test3b_en.jsonl") == set()

    # 명령행 changed: 검색 기록 파일들 → 데이터셋<TAB>id 줄(LF)
    floors_path = tmp_path / "floors.json"
    floors_path.write_text(json.dumps({"candidate_floors": floors}), encoding="utf-8")
    retrieval_paths = []
    for record in (en, ko):
        path = tmp_path / f"{record['dataset']}.retrieval.jsonl"
        path.write_text(json.dumps(record) + "\n", encoding="utf-8")
        retrieval_paths.append(str(path))
    out = tmp_path / "out" / "changed.txt"
    argv = ["eval.refusal", "changed", "--floors", str(floors_path), "--out", str(out), *retrieval_paths]
    monkeypatch.setattr(sys, "argv", argv)
    assert refusal.main() == 0
    assert out.read_bytes() == b"qa_test3b_ko.jsonl\tn010\n"

    without_dataset = {k: v for k, v in ko.items() if k != "dataset"}
    with pytest.raises(ValueError, match="dataset"):
        refusal.changed_ids([without_dataset], floors)


# (c) dev 조건: '판정 4점 이상인데 거절로 분류된' 답이 언어별 1개까지면 test 후보.
def test_dev_command_counts_false_refusals():
    def pair(item_id, answer, score, language="en"):
        return (
            ("d", item_id),
            (
                {
                    "id": item_id,
                    "language": language,
                    "answer": answer,
                    "refusal": refusal.is_refusal_answer(answer, language),
                    "cited_chunk_numbers": [1],
                },
                {"correctness_score": score},
            ),
        )

    ans = dict([pair("a", "I don't know.", 5), pair("b", "Use Query.", 5), pair("c", "I don't know.", 2)])
    na = dict([pair("n", "I don't know.", 5)])
    result = refusal.dev_command(ans, na)
    assert result["languages"]["en"]["false_refusals"] == ["a"]
    assert result["c_adopted_for_test"] is True
    ans.update(dict([pair("e", "I don't know.", 4)]))
    assert refusal.dev_command(ans, na)["c_adopted_for_test"] is False


# test 조건 F1~F4. 다시 생성하지 않은 문항은 기준 답을 후보에도 쓴다.
def test_test_command_conditions():
    def rec(item_id, answer, language="ko", kana=False):
        return {
            "id": item_id,
            "language": language,
            "answer": answer,
            "kana_han": kana,
            "refusal": refusal.is_refusal_answer(answer, language),
            "cited_chunk_numbers": [1],
        }

    base_na = {
        ("na", f"n{i}"): (rec(f"n{i}", "FastAPI는 이렇게 합니다."), {"correctness_score": 2})
        for i in range(4)
    }
    cand_na = {
        ("na", f"n{i}"): (rec(f"n{i}", "모르겠습니다. 문서에 내용이 없습니다."), None) for i in range(3)
    }
    used = [_retrieval("t1", [0.95, 0.9], {1}), _retrieval("t2", [0.95, 0.91], {2})]
    result = refusal.test_command({"ko": 0.9}, base_na, cand_na, {}, {}, used, c_adopted=True)
    assert result["refusals"] == {"base": 0, "cand": 3}
    assert result["conditions"]["F1_refusal_gain"] is True
    assert result["gold_lost_used_sets"] == {"ko": 0}
    assert result["adopt_floor_and_refusal"] is True
    assert result["refusals_with_citations"]["cand"] == 0
    # 정답 손실 2문항이면 F2에서 떨어진다.
    used = [_retrieval("t1", [0.95, 0.85], {2}), _retrieval("t2", [0.95, 0.86], {2})]
    assert (
        refusal.test_command({"ko": 0.9}, base_na, cand_na, {}, {}, used, True)["conditions"]["F2_gold_lost"]
        is False
    )


# --- 저장된 v15 I4 기록 재집계: 거절 분류기를 바꿔도 공개 수치가 조용히 바뀌지 않게 ---
# eval/refusal.py는 생성 기록의 refusal 필드 대신 늘 지금 분류기로 거절을 다시 센다(docs/experiments.md v15
# 규칙 변경 2026-10-18). 그래서 분류기가 바뀌면 커밋된 결정 파일(eval/runs/v15_i4_dev.json,
# v15_i4_test.json)과 README의 거절률(영어 20/20, 한국어 7/20)이 소리 없이 어긋날 수 있다. 저장된 생성·판정·
# 검색 기록을 v15 I4 실행과 같은 인자로 다시 넣어 결정 파일과 모든 항목이 같은지 고정한다. 달라지면 분류기
# 변경이 기록 수치에 닿은 것이니, 수치를 고치지 말고 docs/experiments.md에 날짜 붙인 정정 행을 더한 뒤 이
# 기대값을 그 기록과 함께 바꾼다. 커밋된 파일만 읽으므로 DB·Ollama 없이 돈다.
I4_RUNS = Path(refusal.__file__).parent / "runs"
I4_LABEL = "J1v15"  # I4의 결정 판정 라벨(같은 순서 3회 중앙값)
# I4 test의 F2·F3에 쓴 '이미 쓴 답 있는 test 셋' 여섯 개(236문항). 검색 기록 v15_i4_ret_*, 두 팔의 생성 기록
# v15_i4_ubase_*(기준)·v15_i4_ucand_*(후보)가 같은 이름을 쓴다.
I4_USED_TEST_SETS = ["qa_dataset", "qa_test2", "qa_test2_ko", "qa_test3a_ko", "qa_test3b_en", "qa_test3b_ko"]


# 커밋된 생성 기록(.gen.jsonl)과 J1v15 판정을 eval/refusal.py의 로더로 읽는다.
def _i4_answers(names: list[str]) -> dict:
    return refusal.load_answers([I4_RUNS / f"{name}.gen.jsonl" for name in names], I4_LABEL)


# dev: 답 있는 pool4 dev 80문항과 답 없는 dev 20문항을 다시 세면 커밋된 (c) 판단과 같다 — '판정 4 이상인데
# 거절'은 영어 e4055 하나·한국어 0이라 (c)는 test 후보이고, 답 없는 dev의 거절은 영어 10/10·한국어 6/10.
def test_i4_dev_retally_matches_the_committed_decision():
    result = refusal.dev_command(
        _i4_answers(["v15_i4_base_qa_pool4_dev_en", "v15_i4_base_qa_pool4_dev_ko"]),
        _i4_answers(["v15_i4_base_qa_pool4_na_dev_en", "v15_i4_base_qa_pool4_na_dev_ko"]),
    )
    assert result == read_json(I4_RUNS / "v15_i4_dev.json")
    assert result["languages"]["en"]["false_refusals"] == ["e4055"]
    assert result["languages"]["ko"]["false_refusals"] == []
    assert result["c_adopted_for_test"] is True
    assert [result["languages"][lang]["unanswerable_refusals"] for lang in ("en", "ko")] == [10, 6]


# test: 기준 팔(지금 시스템)과 후보 팔(바닥값 + 청크 0개 거절)을 다시 세면 커밋된 결정과 같다 — 답 없는 test
# 40문항의 거절은 기준 27(영어 20/20, 한국어 7/20) 대 후보 31, F2·F3 탈락, (c) 채택. README의 거절률은 이
# 기준 팔 값이다.
def test_i4_test_retally_matches_the_committed_decision():
    floors = read_json(I4_RUNS / "v15_i4_floors.json")["candidate_floors"]
    used = [
        r for name in I4_USED_TEST_SETS for r in read_jsonl(I4_RUNS / f"v15_i4_ret_{name}.retrieval.jsonl")
    ]
    result = refusal.test_command(
        floors,
        _i4_answers(["v15_i4_base_qa_pool4_na_test_en", "v15_i4_base_qa_pool4_na_test_ko"]),
        _i4_answers(["v15_i4_cand_qa_pool4_na_test_en", "v15_i4_cand_qa_pool4_na_test_ko"]),
        _i4_answers([f"v15_i4_ubase_{name}" for name in I4_USED_TEST_SETS]),
        _i4_answers([f"v15_i4_ucand_{name}" for name in I4_USED_TEST_SETS]),
        used,
        c_adopted=True,
    )
    assert result == read_json(I4_RUNS / "v15_i4_test.json")
    assert result["refusals_by_language"] == {
        "en": {"base": 20, "cand": 20, "n": 20},
        "ko": {"base": 7, "cand": 11, "n": 20},
    }
    assert result["refusals"] == {"base": 27, "cand": 31}
    assert result["adopt_floor_and_refusal"] is False
    assert result["adopt_empty_citations"] is True


# I4 test에서 id만 적은 목록 때문에 문맥이 그대로인데도 두 팔로 다시 생성된 문항: test3b 영어 5개와 한국어
# 3개(같은 id가 다른 언어 셋에서 문맥이 바뀜). 이 8문항은 두 팔의 J1v15 합이 같아(영어 23·23, 한국어 13·13) F3
# 결과에 영향이 없었다. 데이터셋을 구분해 다시 고르면 54문항이고, 그 위에서도 F3는 그대로 떨어진다(254 → 196,
# 허용 폭 −2). docs/experiments.md I4 test 결과의 '영향 0' 확인을 저장된 기록으로 고정한다.
def test_i4_items_regenerated_through_shared_ids_did_not_move_f3():
    floors = read_json(I4_RUNS / "v15_i4_floors.json")["candidate_floors"]
    changed = {
        pair
        for name in I4_USED_TEST_SETS
        for pair in refusal.changed_ids(read_jsonl(I4_RUNS / f"v15_i4_ret_{name}.retrieval.jsonl"), floors)
    }
    base = _i4_answers([f"v15_i4_ubase_{name}" for name in I4_USED_TEST_SETS])
    cand = _i4_answers([f"v15_i4_ucand_{name}" for name in I4_USED_TEST_SETS])
    regenerated = set(base) & set(cand)
    assert (len(changed), len(regenerated)) == (54, 62)
    assert changed <= regenerated
    extra = regenerated - changed
    assert sorted(extra) == [
        *(("qa_test3b_en.jsonl", i) for i in ("n010", "n050", "n077", "n097", "n115")),
        *(("qa_test3b_ko.jsonl", i) for i in ("n034", "n051", "n061")),
    ]

    # test_command의 F3와 같은 점수: 판정이 없으면(청크 0개) 가장 나쁜 점수로 센다.
    def total(rows: dict, keys, language: str | None = None) -> int:
        return sum(
            (rows[k][1] or {}).get("correctness_score") or refusal.UNJUDGED_SCORE
            for k in keys
            if language is None or rows[k][0]["language"] == language
        )

    # 문맥이 같아도 생성 비결정성으로 답은 6개가 달라졌지만 판정 합은 같았다.
    assert sum(base[k][0]["answer"] != cand[k][0]["answer"] for k in extra) == 6
    assert [total(base, extra, "en"), total(cand, extra, "en")] == [23, 23]
    assert [total(base, extra, "ko"), total(cand, extra, "ko")] == [13, 13]
    assert [total(base, regenerated), total(cand, regenerated)] == [290, 232]  # 기록된 F3
    assert [total(base, changed), total(cand, changed)] == [254, 196]
    assert total(cand, changed) < total(base, changed) - refusal.JUDGE_TOLERANCE


# --- eval/judge_panel.py ---


# 이차 가중 kappa: 완전히 같으면 1, 우연 수준이면 0 근처, 0.5 단위 값(두 판정기 평균)도 받는다.
def test_quadratic_kappa():
    assert judge_panel.quadratic_kappa([1, 2, 3, 4, 5], [1, 2, 3, 4, 5]) == pytest.approx(1.0)
    assert judge_panel.quadratic_kappa([1, 5, 1, 5], [5, 1, 5, 1]) < 0
    assert judge_panel.quadratic_kappa([3, 4, 5], [3.5, 4.5, 5]) > 0.5
    assert judge_panel.quadratic_kappa([4, 4], [4, 4]) is None


def test_spearman_handles_ties():
    assert judge_panel.spearman([1, 2, 3], [10, 20, 30]) == pytest.approx(1.0)
    assert judge_panel.spearman([1, 2, 3], [3, 2, 1]) == pytest.approx(-1.0)
    assert judge_panel.spearman([1, 1, 1], [1, 2, 3]) is None


# 층화 표본: 칸 몫을 채우고, 구간에 문항이 모자라면 다음 구간으로 넘긴다. 같은 seed면 같은 표본.
def test_stratified_sample_fills_the_cells():
    items = []
    for family, language, n in (("qwen", "en", 40), ("qwen", "ko", 40), ("ax", "en", 60), ("ax", "ko", 90)):
        for k in range(n):
            items.append(
                {
                    "key": f"{family}{language}{k}",
                    "family": family,
                    "language": language,
                    "j1": 5 if k % 5 else 3,
                    "length": k,
                }
            )
    sample = judge_panel.stratified_sample(items)
    assert len(sample) == judge_panel.SAMPLE_SIZE
    assert sample == judge_panel.stratified_sample(items)
    assert len({i["key"] for i in sample}) == len(sample)


# 커밋된 판정 패널 표본(라벨러 파일·열쇠 파일)이 저장된 기록에서 고정 seed로 다시 뽑은 표본과 같고, Claude
# 라벨이 표본의 80문항을 같은 순서로 하나씩 덮는지 확인한다(라벨을 붙인 뒤 표본을 바꾸지 않았다는 확인). v15
# 표본은 옛 지문(id, 답, 청크 id)으로 중복을 뺀 모집단에서 뽑았으므로 그 지문(dedup="v15")으로 다시 뽑는다.
def test_committed_panel_sample_and_labels_match_the_sampler():
    runs = Path(judge_panel.__file__).parent / "runs"

    def lines(name: str) -> list[dict]:
        return [json.loads(line) for line in (runs / name).read_text(encoding="utf-8").splitlines()]

    chosen = judge_panel.stratified_sample(judge_panel.population(dedup="v15"))
    keys = lines("v15_i5_panel_key.jsonl")
    assert sorted(k["key"] for k in keys) == sorted(i["key"] for i in chosen)
    assert all(judge_panel.blind_id(k["key"]) == k["sample_id"] for k in keys)
    sample = lines("v15_i5_panel_sample.jsonl")
    sample_ids = [s["sample_id"] for s in sample]
    assert sample_ids == sorted(k["sample_id"] for k in keys)
    assert [label["sample_id"] for label in lines("v15_i5_claude_labels.jsonl")] == sample_ids
    # 라벨러 파일에는 점수·출처가 없다.
    assert all(
        set(s) == {"sample_id", "language", "question", "context_passages", "answer", "reference_answer"}
        for s in sample
    )


# 새 지문(데이터셋, id, 답, 청크 본문)은 다른 DB에서 만든 같은 답(청크 id만 다름)을 한 번만 센다. v15 표본에
# 쓴 옛 지문(id, 답, 청크 id)은 그런 둘을 모두 넣었다(v13b B2의 B0와 v13 채택 G3 한국어가 그랬고, n086이
# 표본에 두 번 들어감). 청크 본문이 다르거나 데이터셋이 다르면 다른 문항이다.
def test_population_counts_an_answer_once_even_when_only_the_chunk_ids_differ(tmp_path, monkeypatch):
    def record(dataset: str, chunk_id: str, content: str = "c") -> dict:
        r = _gen_record("n086", "Path를 쓰세요.", 1000.0, [1])
        r.update(dataset=dataset, chunks=[{"chunk_id": chunk_id, "content": content, "source_path": "a.md"}])
        return r

    files = [
        _write(tmp_path, name, [record(dataset, chunk_id, content)], {"n086": 4})
        for name, dataset, chunk_id, content in (
            ("first", "qa_test3b_ko.jsonl", "1", "c"),
            ("other_db", "qa_test3b_ko.jsonl", "99", "c"),  # 청크 id만 다름: 같은 문항
            ("other_text", "qa_test3b_ko.jsonl", "1", "d"),  # 청크 본문이 다름: 다른 문항
            ("other_set", "qa_test3b_en.jsonl", "1", "c"),  # 데이터셋이 다름: 다른 문항
        )
    ]
    monkeypatch.setattr(judge_panel, "COMPARISONS", {"x": {"a": files}})
    assert [i["key"] for i in judge_panel.population()] == [
        "first.gen.jsonl#n086",
        "other_text.gen.jsonl#n086",
        "other_set.gen.jsonl#n086",
    ]
    assert judge_panel.unique_keys(judge_panel.records_by_key()) == {
        "first.gen.jsonl#n086",
        "other_text.gen.jsonl#n086",
        "other_set.gen.jsonl#n086",
    }
    # 옛 지문은 청크 id만 보므로 청크 id가 같은 셋을 하나로, 다른 DB의 같은 답은 둘로 셌다.
    assert [i["key"] for i in judge_panel.population(dedup="v15")] == [
        "first.gen.jsonl#n086",
        "other_db.gen.jsonl#n086",
    ]
    with pytest.raises(ValueError):
        judge_panel.population(dedup="chunk_ids")


# 길이 상관을 생성기별로 나눈다. 긴 답을 쓰는 생성기(A.X)가 점수도 높으면, 생성기 안에서는 길수록 점수가
# 낮아도 풀링 상관은 양수가 된다(v15 I5의 풀링 값이 생성기와 섞인 이유). 기준 라벨과의 잔차(판정 − 기준)의
# 길이 상관은 기준이 설명하지 못하는 길이 선호만 남긴다.
def test_family_spearman_splits_a_pooled_length_correlation_by_generator():
    keys, families, lengths, scores = [], {}, {}, {}
    for k in range(10):
        for family, base_length, base_score in (("qwen", 100, 3.0), ("ax", 1000, 5.0)):
            key = f"{family}{k}"
            keys.append(key)
            families[key], lengths[key], scores[key] = family, base_length + k, base_score - k * 0.1
    split = judge_panel.family_spearman(keys, lengths, scores, families)
    assert split["all"] > 0.5
    assert split["ax"] == pytest.approx(-1.0)
    assert split["qwen"] == pytest.approx(-1.0)
    residual = {k: lengths[k] / 10_000 for k in keys}  # 기준보다 긴 답에 조금씩 더 준 판정기의 잔차
    assert judge_panel.family_spearman(keys, lengths, residual, families) == pytest.approx(
        {"all": 1.0, "ax": 1.0, "qwen": 1.0}
    )


# kappa 보고: 평균 구성은 J1뿐 아니라 가장 좋은 단독 판정기와도 견준다(같은 입도의 비교. v15 I5의 J2+J3 평균은
# J2 단독보다 0.013 높았을 뿐임). 같은 답·같은 문맥인 표본 문항은 찾아서 보고하고, 뒤의 것을 뺀 kappa를 함께
# 낸다. 잔차-길이 상관은 판정기마다 낸다(J2처럼 기준과 똑같으면 잔차가 모두 0이라 None).
def test_kappa_report_compares_averages_with_the_best_single_judge_and_drops_duplicates(tmp_path):
    gold = [1, 2, 3, 4, 5, 1, 2, 3, 4, 5, 3, 3]
    records, keys = {}, {}
    for k in range(11):
        key = f"f.gen.jsonl#q{k}"
        records[key] = {
            "id": f"q{k}",
            "dataset": "d.jsonl",
            "answer": "x" * (10 + k),
            "model": "a.x-4.0-light",
            "chunks": [{"chunk_id": str(k), "content": f"c{k}"}],
        }
        keys[f"s{k:02d}"] = key
    # s11은 s10과 같은 답·같은 문맥(다른 파일, 다른 청크 id)
    records["g.gen.jsonl#q10"] = {
        **records["f.gen.jsonl#q10"],
        "chunks": [{"chunk_id": "99", "content": "c10"}],
    }
    keys["s11"] = "g.gen.jsonl#q10"
    noisy = [2, 2, 3, 5, 5, 1, 3, 3, 4, 4, 3, 3]
    scores = {
        "J1": {keys[s]: 6 - g for s, g in zip(sorted(keys), gold, strict=True)},
        "J2": {keys[s]: g for s, g in zip(sorted(keys), gold, strict=True)},
        "J3": {keys[s]: n for s, n in zip(sorted(keys), noisy, strict=True)},
    }
    claude_path, key_path = tmp_path / "claude.jsonl", tmp_path / "key.jsonl"
    claude_path.write_text(
        "".join(
            json.dumps({"sample_id": s, "correctness_score": g}) + "\n"
            for s, g in zip(sorted(keys), gold, strict=True)
        ),
        encoding="utf-8",
    )
    key_path.write_text(
        "".join(json.dumps({"sample_id": s, "key": keys[s]}) + "\n" for s in sorted(keys)), encoding="utf-8"
    )

    result = judge_panel.kappa_report(["J1", "J2", "J3"], scores, claude_path, key_path, records)
    configs = result["configs"]
    assert result["n"] == 12
    assert configs["J1"]["diff_vs_j1_ci90"] == [0.0, 0.0]
    assert configs["J2"]["kappa"] == pytest.approx(1.0)
    assert configs["J2+J3"]["best_single"] == "J2"
    low, high = configs["J2+J3"]["diff_vs_best_single_ci90"]
    assert low <= high <= 0  # 기준과 똑같은 J2보다 나을 수 없다
    assert all("best_single" not in configs[label] for label in ("J1", "J2", "J3"))
    assert result["duplicates"] == [["s10", "s11"]]
    assert result["dedup"]["n"] == 11
    assert set(result["dedup"]["kappa"]) == set(configs)
    assert set(result["residual_length_spearman"]) == {"J1", "J2", "J3"}
    assert result["residual_length_spearman"]["J2"]["all"] is None
    assert set(result["reference_length_spearman"]) == {"all", "ax", "qwen"}


# 커밋된 v15 표본(옛 지문으로 뽑음)에는 같은 답·같은 문맥이 한 쌍 있다: n086(v13 채택 G3 한국어 raw와 v13b
# B2의 B0 lg, 청크 id만 다름). 새 지문은 이 쌍만 찾고, 뒤의 것을 빼고 다시 세도 모든 구성의 kappa 변화가 0.003
# 이하다(docs/experiments.md I5 결과의 2026-10-29 추가 분석). bootstrap 없이 kappa 값만 비교한다.
def test_committed_panel_sample_has_one_duplicate_pair_that_barely_moves_kappa():
    def lines(name: str) -> list[dict]:
        return read_jsonl(judge_panel.RUNS / name)

    records = judge_panel.records_by_key()
    # 저장된 답 448개 중 새 지문으로는 402개, 옛 지문으로는 447개가 서로 다른 문항이다(population 주석의 수).
    assert len(records) == 448
    assert len(judge_panel.unique_keys(records)) == 402
    assert len(judge_panel.unique_keys(records, dedup="v15")) == 447
    keys = {k["sample_id"]: k["key"] for k in lines("v15_i5_panel_key.jsonl")}
    claude = {c["sample_id"]: float(c["correctness_score"]) for c in lines("v15_i5_claude_labels.jsonl")}
    ids = sorted(claude)
    groups = judge_panel.duplicate_groups(ids, keys, records)
    assert [[keys[s] for s in group] for group in groups] == [
        ["v13_adopt_g3_qa_test3b_ko.raw.gen.jsonl#n086", "v13b_b2_g3_b0.lg.gen.jsonl#n086"]
    ]
    labels = ["J1v15", "J2v15", "J3v15"]
    scores = {label: judge_panel.scores_for(label) for label in labels}
    kept = [s for s in ids if s != groups[0][1]]
    full = judge_panel.judge_configs(labels, scores, keys, ids)
    dedup = judge_panel.judge_configs(labels, scores, keys, kept)
    assert set(full) == {
        "J1v15",
        "J2v15",
        "J3v15",
        "J1v15+J2v15",
        "J1v15+J3v15",
        "J2v15+J3v15",
        "J1v15+J2v15+J3v15",
    }
    for name, values in full.items():
        before = judge_panel.quadratic_kappa([claude[i] for i in ids], values)
        after = judge_panel.quadratic_kappa([claude[i] for i in kept], dedup[name])
        assert abs(after - before) <= 0.003, name

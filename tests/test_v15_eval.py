"""v15 평가 도구(판정 흔들림 진단, 인용 호출 비교, 거절·바닥값, 판정 패널)를 가짜 기록으로 검증한다.

docs/experiments.md v15의 결정 규칙이 코드와 같은지 고정한다. DB·Ollama 없이 돈다.
"""

# [테스트 묶음] eval/judge_stability.py, eval/citation_arms.py, eval/refusal.py, eval/judge_panel.py의 순수
# 함수와, eval/judge.py에 더한 think·캐시 되돌리기 요청 본문.
# [왜 중요한가] 이 도구들은 측정 전에 등록한 규칙을 그대로 옮긴 것이다. 규칙과 다르게 세면 측정 뒤에 결정이
# 바뀌므로, 경계값(같음/다름, 허용 폭의 끝)을 가짜 기록으로 고정한다.

import json
from pathlib import Path

import pytest

from eval import citation_arms, judge_panel, judge_stability, refusal
from eval.judge import (
    FLUSH_MESSAGES,
    JudgeConfig,
    answer_sha1,
    judge_items,
    ollama_flush_payload,
    ollama_judge_payload,
)

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
# 라벨이 표본의 80문항을 같은 순서로 하나씩 덮는지 확인한다(라벨을 붙인 뒤 표본을 바꾸지 않았다는 확인).
def test_committed_panel_sample_and_labels_match_the_sampler():
    runs = Path(judge_panel.__file__).parent / "runs"

    def lines(name: str) -> list[dict]:
        return [json.loads(line) for line in (runs / name).read_text(encoding="utf-8").splitlines()]

    chosen = judge_panel.stratified_sample(judge_panel.population())
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

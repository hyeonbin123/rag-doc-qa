"""The v13 generation-model comparison: guard arms, per-item metrics, the gate, summaries.

docs/experiments.md v13 runs every selection and adoption generation with the language
guard on and records the first (unguarded) answer next to the final one, so one run gives
two arms: the generator alone ("raw", what a run without the guard returns) and the
generator with the guard ("lg"). These tests pin how the two arms are derived and counted.
No Ollama or database is needed.
"""

import json
import uuid

import pytest

from eval import generator_arms
from eval.common import read_json, read_jsonl, write_json, write_jsonl


def calls(*done_reasons, thinking=0, eval_count=50, prompt=1500):
    return [
        {
            "prompt_eval_count": prompt,
            "eval_count": eval_count,
            "done_reason": d,
            "thinking_chars": thinking,
            "ms": 900.0,
        }
        for d in done_reasons
    ]


def gen(item_id, answer="답입니다.", language="ko", dataset="qa_dev_ko.jsonl", **extra):
    record = {
        "id": item_id,
        "dataset": dataset,
        "dataset_index": int(item_id[1:]),
        "run_tag": "unit",
        "question": "질문?" if language == "ko" else "Question?",
        "language": language,
        "reference_answer": "Ref.",
        "expected_source_paths": ["docs/ko/docs/p1.md"],
        "must_include_keywords": ["Query"],
        "chunks": [
            {
                "rank": n,
                "chunk_id": str(uuid.uuid4()),
                "source_path": f"docs/{language}/docs/p{n}.md",
                "content": "c",
            }
            for n in (1, 2, 3)
        ],
        "answer": answer,
        "cited_chunk_numbers": [1],
        "generation_ms": 3000.0,
        "keyword_coverage": 0.0,
        "kana_han": False,
        "guard_applied": False,
        "generation_calls": {"answer": calls("stop"), "citation": calls("stop")[0]},
        "citation_schema_error": None,
        "think_tag_in_answer": False,
    }
    record.update(extra)
    return record


GUARDED = dict(
    answer="`Query` 답입니다.",
    guard_applied=True,
    unguarded_answer="답입니다. 中文으로 다시",
    guard_retry_ms=1200.0,
    generation_ms=4200.0,
    kana_han=False,
    keyword_coverage=1.0,
    generation_calls={"answer": calls("length", "stop"), "citation": calls("stop")[0]},
)


def test_the_raw_arm_is_the_first_answer_call():
    raw = generator_arms.unguarded_record(gen("k1", **GUARDED))

    assert raw["arm"] == "raw"
    assert raw["answer"] == "답입니다. 中文으로 다시"
    assert raw["kana_han"] is True
    assert raw["keyword_coverage"] == 0.0
    assert raw["generation_ms"] == pytest.approx(3000.0)  # the retry is not part of this arm
    assert raw["answer_done_reason"] == "length"
    assert raw["cited_chunk_numbers"] is None  # the citation call saw the final answer


def test_the_lg_arm_is_the_final_answer_and_unguarded_items_are_shared():
    lg = generator_arms.guarded_record(gen("k1", **GUARDED))
    plain = gen("k2")

    assert lg["arm"] == "lg"
    assert lg["answer"] == "`Query` 답입니다."
    assert lg["answer_done_reason"] == "stop"
    assert lg["generation_ms"] == 4200.0
    raw2, lg2 = generator_arms.unguarded_record(plain), generator_arms.guarded_record(plain)
    assert raw2["answer"] == lg2["answer"] == plain["answer"]
    assert raw2["cited_chunk_numbers"] == lg2["cited_chunk_numbers"] == [1]


def test_split_writes_both_arm_files_with_their_run_notes(tmp_path):
    gen_path = tmp_path / "v13_unit_g0_qa_dev_ko.gen.jsonl"
    write_jsonl(gen_path, [gen("k1", **GUARDED), gen("k2")])
    write_json(tmp_path / "v13_unit_g0_qa_dev_ko.gen.meta.json", {"model": "m", "language_guard": True})

    raw_path, lg_path = generator_arms.split_file(gen_path)

    assert raw_path.name == "v13_unit_g0_qa_dev_ko.raw.gen.jsonl"
    assert lg_path.name == "v13_unit_g0_qa_dev_ko.lg.gen.jsonl"
    assert [r["answer"] for r in read_jsonl(raw_path)] == ["답입니다. 中文으로 다시", "답입니다."]
    assert read_json(tmp_path / "v13_unit_g0_qa_dev_ko.raw.gen.meta.json")["arm"] == "raw"
    lg_meta = read_json(tmp_path / "v13_unit_g0_qa_dev_ko.lg.gen.meta.json")
    assert lg_meta["arm"] == "lg" and lg_meta["derived_from"].endswith("v13_unit_g0_qa_dev_ko.gen.jsonl")


def test_split_refuses_a_run_made_without_the_guard(tmp_path):
    gen_path = tmp_path / "x.gen.jsonl"
    write_jsonl(gen_path, [gen("k1")])
    write_json(tmp_path / "x.gen.meta.json", {"language_guard": False})

    with pytest.raises(ValueError, match="guard"):
        generator_arms.split_file(gen_path)


def test_item_row_checks_citations_against_the_passages():
    judgment = {"id": "k1", "correctness_score": 4, "faithfulness_score": 3, "hallucinated": False}

    ok = generator_arms.item_row(generator_arms.guarded_record(gen("k1")), judgment)
    out_of_range = generator_arms.item_row(
        generator_arms.guarded_record(gen("k1", cited_chunk_numbers=[2, 7])), judgment
    )
    unknown = generator_arms.item_row(generator_arms.unguarded_record(gen("k1", **GUARDED)), judgment)

    assert ok["citations_in_range"] is True and ok["cites_expected_page"] is True
    assert out_of_range["citations_in_range"] is False and out_of_range["cites_expected_page"] is False
    assert unknown["citations_in_range"] is None and unknown["cites_expected_page"] is None
    assert unknown["done_length"] is True and unknown["kana_han"] is True
    assert ok["correctness"] == 4 and ok["hallucinated"] is False


def test_summary_counts_by_language():
    rows = [
        {
            "language": "en",
            "correctness": 5,
            "faithfulness": 4,
            "hallucinated": False,
            "kana_han": False,
            "generation_ms": 2000.0,
            "done_length": False,
            "thinking": False,
            "citation_error": False,
            "citations_in_range": True,
            "cites_expected_page": True,
            "guard_applied": False,
            "judged": True,
        },
        {
            "language": "ko",
            "correctness": 3,
            "faithfulness": 3,
            "hallucinated": True,
            "kana_han": True,
            "generation_ms": 4000.0,
            "done_length": True,
            "thinking": False,
            "citation_error": True,
            "citations_in_range": None,
            "cites_expected_page": None,
            "guard_applied": True,
            "judged": True,
        },
        {
            "language": "ko",
            "correctness": 4,
            "faithfulness": 4,
            "hallucinated": False,
            "kana_han": False,
            "generation_ms": 3000.0,
            "done_length": False,
            "thinking": True,
            "citation_error": False,
            "citations_in_range": True,
            "cites_expected_page": False,
            "guard_applied": False,
            "judged": True,
        },
    ]

    s = generator_arms.summarize(rows)

    assert (
        s["all"]["correctness_sum"] == 12
        and s["en"]["correctness_sum"] == 5
        and s["ko"]["correctness_sum"] == 7
    )
    assert s["all"]["hallucinated"] == 1 and s["ko"]["kana_han"] == 1
    assert s["all"]["generation_p50_ms"] == 3000.0
    assert s["all"]["done_length"] == 1 and s["all"]["thinking"] == 1 and s["all"]["citation_errors"] == 1
    assert s["all"]["citations_in_range"] == "2/2" and s["all"]["cites_expected_page"] == "1/2"
    assert s["ko"]["guard_applied"] == 1


def write_gate_run(tmp_path, records, meta):
    gen_path = tmp_path / "v13_gate_x_qa_dev_ko.gen.jsonl"
    write_jsonl(gen_path, records)
    write_json(tmp_path / "v13_gate_x_qa_dev_ko.gen.meta.json", meta)
    return gen_path


GATE_META = {
    "model": "m:tag",
    "model_digest": "abc123",
    "language_guard": False,
    "ollama_ps_after": {"models": [{"name": "m:tag", "size": 100, "size_vram": 100, "context_length": 8192}]},
}


def test_gate_passes_a_clean_run(tmp_path):
    records = [gen(f"k{i}", generation_prompt_tokens_counted=1500) for i in range(1, 13)]
    result = generator_arms.gate(write_gate_run(tmp_path, records, GATE_META), digest="abc123")

    assert result["passed"] is True
    assert result["checks"]["full_gpu"]["ok"] and result["checks"]["digest"]["ok"]
    assert result["prompt_count"]["max_abs_diff"] == 0


@pytest.mark.parametrize(
    ("change", "failed"),
    [
        (
            {"meta": {"ollama_ps_after": {"models": [{"name": "m:tag", "size": 100, "size_vram": 88}]}}},
            "full_gpu",
        ),
        ({"meta": {"model_digest": "zzz"}}, "digest"),
        (
            {
                "record": {
                    "generation_calls": {"answer": calls("stop", thinking=12), "citation": calls("stop")[0]}
                }
            },
            "no_thinking",
        ),
        ({"record": {"think_tag_in_answer": True}}, "no_thinking"),
        ({"record": {"citation_schema_error": "not JSON"}}, "citations_first_10"),
        ({"records_length": 2}, "done_length"),
        ({"record": {"generation_ms": 12000.0}, "all": True}, "p50"),
    ],
)
def test_gate_fails_each_condition(tmp_path, change, failed):
    records = [gen(f"k{i}") for i in range(1, 13)]
    if "record" in change:
        targets = records if change.get("all") else records[:1]
        for r in targets:
            r.update(change["record"])
    for r in records[: change.get("records_length", 0)]:
        r["generation_calls"] = {"answer": calls("length"), "citation": calls("stop")[0]}
    meta = {**GATE_META, **change.get("meta", {})}

    result = generator_arms.gate(write_gate_run(tmp_path, records, meta), digest="abc123")

    assert result["passed"] is False
    assert result["checks"][failed]["ok"] is False
    assert [name for name, c in result["checks"].items() if not c["ok"]] == [failed]


def test_gate_can_require_ollama_and_tokenizer_prompt_counts_to_agree(tmp_path):
    records = [gen(f"k{i}", generation_prompt_tokens_counted=1500) for i in range(1, 13)]
    records[3]["generation_prompt_tokens_counted"] = 1460  # Ollama read 1500: 40 more than the template gives

    loose = generator_arms.gate(write_gate_run(tmp_path, records, GATE_META), digest="abc123")
    strict = generator_arms.gate(
        write_gate_run(tmp_path, records, GATE_META), digest="abc123", require_prompt_match=True
    )

    assert loose["passed"] is True and loose["prompt_count"]["max_abs_diff"] == 40
    assert strict["passed"] is False and strict["checks"]["prompt_match"]["ok"] is False


def test_the_prompt_match_tolerance_catches_a_missing_assistant_header(tmp_path):
    # A Modelfile template that drops "<|im_start|><|assistant|>" reads 2 tokens fewer.
    records = [gen(f"k{i}", generation_prompt_tokens_counted=1500) for i in range(1, 13)]
    records[0]["generation_prompt_tokens_counted"] = 1502
    path = write_gate_run(tmp_path, records, GATE_META)

    within_16 = generator_arms.gate(path, digest="abc123", require_prompt_match=True)
    within_1 = generator_arms.gate(path, digest="abc123", require_prompt_match=True, prompt_tolerance=1)

    assert within_16["checks"]["prompt_match"]["ok"] is True
    assert within_1["checks"]["prompt_match"]["ok"] is False


def test_arm_files_pair_with_their_judgments(tmp_path):
    gen_path = tmp_path / "v13_sel_g0_qa_dev_ko.raw.gen.jsonl"
    write_jsonl(gen_path, [generator_arms.unguarded_record(gen("k1"))])
    judged = tmp_path / "v13_sel_g0_qa_dev_ko.raw.J1.judge.jsonl"
    write_jsonl(
        judged, [{"id": "k1", "correctness_score": 5, "faithfulness_score": 4, "hallucinated": False}]
    )

    rows = generator_arms.arm_rows([gen_path], "J1")

    assert rows[0]["correctness"] == 5 and rows[0]["dataset"] == "qa_dev_ko.jsonl"
    assert json.loads(json.dumps(rows))  # plain data, kept in the summary JSON

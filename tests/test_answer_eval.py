"""The answer eval's judge call, truncation check, per-item records and comparisons.

Until v10 the Ollama judge call set only temperature 0, so it ran in Ollama's default
4096-token context, and Ollama cuts an over-long prompt without saying so. These tests
pin the v11 judge (num_ctx 8192, truncate=false, a pre-flight length check, the
prompt_eval_count kept next to a tokenizer count), the legacy judge kept for comparison,
and the per-item JSONL that lets a judge rerun without regenerating answers. No Ollama,
database or tokenizer download is needed.
"""

import json
import uuid

import httpx
import pytest

from app.services.generation import GenerationResult
from app.services.retrieval import RetrievedChunk
from eval import compare_judgments, judge, run_answer_eval, run_judge
from eval.common import EvalQuestion, read_jsonl, write_jsonl
from eval.judge import (
    JUDGE_SCHEMA,
    JudgeConfig,
    JudgeContextError,
    JudgeOutcome,
    build_judge_prompt,
    judge_items,
    judge_with_ollama,
    ollama_judge_payload,
    truncation_status,
)
from eval.tokens import ChatTokenCounter

GOOD_SCORES = {"faithfulness_score": 4, "hallucinated": False, "correctness_score": 5}


def mock_ollama(monkeypatch, handler):
    real_client = httpx.AsyncClient
    monkeypatch.setattr(
        judge.httpx,
        "AsyncClient",
        lambda **kwargs: real_client(transport=httpx.MockTransport(handler), **kwargs),
    )


def chat_response(content: dict | str, prompt_eval_count: int = 1234) -> httpx.Response:
    body = content if isinstance(content, str) else json.dumps(content)
    return httpx.Response(
        200,
        json={
            "message": {"role": "assistant", "content": body},
            "prompt_eval_count": prompt_eval_count,
            "eval_count": 30,
            "done_reason": "stop",
        },
    )


def gen_record(item_id: str, answer: str = "Use Query().", chunks: int = 2, **extra) -> dict:
    record = {
        "id": item_id,
        "dataset": "qa_test2.jsonl",
        "dataset_index": int(item_id[1:]) if item_id[1:].isdigit() else 0,
        "run_tag": "unit",
        "question": f"Question {item_id}?",
        "reference_answer": "Reference.",
        "chunks": [
            {"rank": n, "chunk_id": str(uuid.uuid4()), "source_path": f"p{n}.md", "content": f"Passage {n}."}
            for n in range(1, chunks + 1)
        ],
        "answer": answer,
    }
    record.update(extra)
    return record


# --- the judge call -------------------------------------------------------------------


def test_v11_judge_asks_for_8192_tokens_and_no_silent_truncation():
    payload = ollama_judge_payload("prompt", JudgeConfig(model="qwen2.5:7b-instruct"))

    assert payload["options"] == {"temperature": 0, "num_ctx": 8192}
    assert payload["truncate"] is False
    assert payload["format"] == JUDGE_SCHEMA
    assert payload["messages"] == [{"role": "user", "content": "prompt"}]
    assert payload["stream"] is False


def test_legacy_judge_payload_is_the_pre_v11_one():
    # J0 must reproduce the old call exactly: Ollama's default context, default truncation.
    payload = ollama_judge_payload("prompt", JudgeConfig(model="m", num_ctx=None, label="J0"))

    assert payload == {
        "model": "m",
        "messages": [{"role": "user", "content": "prompt"}],
        "format": JUDGE_SCHEMA,
        "stream": False,
        "options": {"temperature": 0},
    }


def test_judge_prompt_text_is_unchanged():
    prompt = build_judge_prompt("Q?", "ctx", "ans", "ref")

    assert prompt == (
        "Question: Q?\n\n"
        "Context passages the model was given:\nctx\n\n"
        "Model's answer:\nans\n\n"
        "Reference answer:\nref\n\n"
        "Score the model's answer. Both scores use a 1-5 scale, where 1 is worst and 5 is best."
    )


async def test_judge_keeps_raw_reply_and_prompt_eval_count(monkeypatch):
    sent = []

    def handler(request):
        sent.append(json.loads(request.content))
        return chat_response(GOOD_SCORES, prompt_eval_count=2222)

    mock_ollama(monkeypatch, handler)
    outcome = await judge_with_ollama("http://ollama.test", "prompt", JudgeConfig(model="m"))

    assert sent[0]["options"]["num_ctx"] == 8192
    assert (outcome.faithfulness_score, outcome.hallucinated, outcome.correctness_score) == (4, False, 5)
    assert json.loads(outcome.raw) == GOOD_SCORES
    assert (outcome.prompt_eval_count, outcome.eval_count, outcome.done_reason) == (2222, 30, "stop")
    assert outcome.error is None


async def test_judge_still_rejects_scores_off_the_scale(monkeypatch):
    mock_ollama(monkeypatch, lambda request: chat_response({**GOOD_SCORES, "correctness_score": 9}))

    with pytest.raises(ValueError, match="correctness_score=9"):
        await judge_with_ollama("http://ollama.test", "prompt", JudgeConfig(model="m"))


async def test_context_overflow_error_is_recorded_not_raised(monkeypatch):
    # With truncate=false Ollama refuses an over-long prompt; the item is kept as an error.
    mock_ollama(
        monkeypatch,
        lambda request: httpx.Response(400, json={"error": "the input length exceeds the context length"}),
    )

    outcome = await judge_with_ollama("http://ollama.test", "prompt", JudgeConfig(model="m"))

    assert outcome.correctness_score is None
    assert "exceeds the context length" in outcome.error


async def test_other_ollama_errors_still_raise(monkeypatch):
    mock_ollama(monkeypatch, lambda request: httpx.Response(500, json={"error": "model runner crashed"}))

    with pytest.raises(httpx.HTTPStatusError):
        await judge_with_ollama("http://ollama.test", "prompt", JudgeConfig(model="m"))


# --- truncation detection --------------------------------------------------------------


def test_truncation_status_compares_evaluated_and_counted_tokens():
    assert truncation_status(prompt_eval_count=5000, counted_tokens=5003) == "ok"
    # Ollama 0.35.1 keeps 4 tokens plus about half of a 4096 window.
    assert truncation_status(prompt_eval_count=2050, counted_tokens=5003) == "truncated"
    assert truncation_status(prompt_eval_count=None, counted_tokens=5003) == "unchecked"
    assert truncation_status(prompt_eval_count=2050, counted_tokens=None) == "unchecked"


async def test_judge_items_records_counts_flags_and_answer_hash():
    records = [gen_record("t1"), gen_record("t2", answer="A longer answer.")]
    evaluated = {"Question t1?": 300, "Question t2?": 100}  # t2 comes back short

    async def call(prompt):
        question = prompt.split("\n")[0].removeprefix("Question: ")
        return JudgeOutcome(**GOOD_SCORES, raw="{}", prompt_eval_count=evaluated[question])

    judgments = await judge_items(records, JudgeConfig(model="m"), call, count_tokens=lambda messages: 300)

    assert [j["id"] for j in judgments] == ["t1", "t2"]
    assert [j["truncation"] for j in judgments] == ["ok", "truncated"]
    assert judgments[0]["prompt_tokens_counted"] == 300
    assert judgments[0]["judge_label"] == "J1"
    assert judgments[0]["judge_num_ctx"] == 8192
    assert judgments[0]["judge_truncate"] is False
    assert judgments[0]["answer_sha1"] != judgments[1]["answer_sha1"]
    assert judgments[1]["order_index"] == 1


async def test_judge_items_checks_every_prompt_fits_before_sending():
    calls = []

    async def call(prompt):
        calls.append(prompt)
        return JudgeOutcome(**GOOD_SCORES)

    with pytest.raises(JudgeContextError, match="t2"):
        await judge_items(
            [gen_record("t1"), gen_record("t2", answer="x " * 50)],
            JudgeConfig(model="m", num_ctx=8192),
            call,
            count_tokens=lambda messages: 8000 if "x x" in messages[0]["content"] else 500,
        )
    assert calls == []  # nothing sent: the run stops before the first judge call


async def test_legacy_judge_items_send_over_long_prompts_to_measure_truncation():
    async def call(prompt):
        return JudgeOutcome(**GOOD_SCORES, prompt_eval_count=2050)

    judgments = await judge_items(
        [gen_record("t1")], JudgeConfig(model="m", num_ctx=None, label="J0"), call, lambda m: 6000
    )

    assert judgments[0]["truncation"] == "truncated"
    assert judgments[0]["judge_num_ctx"] is None
    assert judgments[0]["judge_truncate"] is None


async def test_judge_items_skip_questions_without_context():
    async def call(prompt):
        raise AssertionError("no judge call without passages")

    judgments = await judge_items([gen_record("t1", chunks=0)], JudgeConfig(model="m"), call, None)

    assert judgments[0]["correctness_score"] is None
    assert judgments[0]["truncation"] == "unchecked"


def test_chat_token_counter_counts_the_templated_prompt():
    class FakeTokenizer:
        def apply_chat_template(self, messages, tokenize, add_generation_prompt):
            assert tokenize is False and add_generation_prompt is True
            return "<sys>" + "".join(m["content"] for m in messages) + "<asst>"

        def __call__(self, text, add_special_tokens):
            assert add_special_tokens is False
            return {"input_ids": list(range(len(text.split("|"))))}

    counter = ChatTokenCounter(FakeTokenizer())

    assert counter([{"role": "user", "content": "a|b|c"}]) == 3


# --- per-item generation records ------------------------------------------------------


async def test_generation_record_keeps_ranked_chunks_answer_and_timing(monkeypatch):
    chunks = [
        RetrievedChunk(uuid.uuid4(), uuid.uuid4(), f"docs/en/docs/p{n}.md", f"H{n}", f"Text {n}", 1 - n / 10)
        for n in range(1, 4)
    ]

    async def fake_retrieve(db, question, vector, top_k, mode, **kwargs):
        return chunks

    class FakeGenerator:
        async def answer(self, question, retrieved, language="en"):
            return GenerationResult("Use Query().", [1], 900, 40, "local-model")

    class FakeEmbedder:
        model_name = "fake-embedding"

        def embed_query(self, text):
            return [0.0]

    monkeypatch.setattr(run_answer_eval, "retrieve", fake_retrieve)
    q = EvalQuestion(
        id="t1",
        question="How do I read a query parameter?",
        expected_source_paths=["docs/en/docs/p2.md"],
        reference_answer="Declare it.",
        must_include_keywords=["Query"],
    )

    record = await run_answer_eval.generate_answer(
        None, lambda lang: FakeEmbedder(), FakeGenerator(), q, 5, "dense", None
    )

    assert [c["rank"] for c in record["chunks"]] == [1, 2, 3]
    assert record["chunks"][0]["chunk_id"] == str(chunks[0].chunk_id)
    assert record["chunks"][1]["content"] == "Text 2"
    assert record["first_hit_rank"] == 2
    assert record["answer"] == "Use Query()."
    assert record["reference_answer"] == "Declare it."
    assert record["generation_ms"] >= 0
    assert (record["generation_input_tokens"], record["generation_output_tokens"]) == (900, 40)
    assert record["keyword_coverage"] == 1.0
    assert judge.judge_context(record) == "Text 1\n\nText 2\n\nText 3"



async def test_generation_counts_the_other_translation_as_a_hit_and_crosses_only_korean(monkeypatch):
    chunk = RetrievedChunk(uuid.uuid4(), uuid.uuid4(), "docs/en/docs/p1.md", "H", "Text", 0.8)
    calls: list[dict] = []

    async def fake_retrieve(db, question, vector, top_k, mode, **kwargs):
        calls.append(kwargs)
        return [chunk]

    class FakeGenerator:
        async def answer(self, question, retrieved, language="en"):
            return GenerationResult("답", [1], 10, 5, "local-model")

    class FakeEmbedder:
        model_name = "fake-embedding"

        def embed_query(self, text):
            return [0.0]

    monkeypatch.setattr(run_answer_eval, "retrieve", fake_retrieve)
    ko = EvalQuestion("n1", "본문은 어떻게 받나요?", ["docs/ko/docs/p1.md"], "모델로.", [])
    en = EvalQuestion("t1", "How do I read a body?", ["docs/en/docs/p1.md"], "A model.", [])

    ko_record = await run_answer_eval.generate_answer(
        None, lambda lang: FakeEmbedder(), FakeGenerator(), ko, 5, "dense", None,
        cross_lingual=True, score_floor=0.2,
    )
    await run_answer_eval.generate_answer(
        None, lambda lang: FakeEmbedder(), FakeGenerator(), en, 5, "dense", None, cross_lingual=True
    )

    assert ko_record["first_hit_rank"] == 1  # the English page of the expected Korean one
    assert ko_record["cross_lingual"] is True
    assert ko_record["score_floor"] == 0.2
    assert calls[0]["cross_lingual"] is True and calls[0]["score_floor"] == 0.2
    assert calls[1]["cross_lingual"] is False  # English questions search English only
    assert calls[1]["score_floor"] == 0.3  # the model's floor when none is given

def test_generation_order_is_the_dataset_order_or_a_seeded_shuffle():
    assert run_answer_eval.generation_order(5, "dataset", seed=1) == [0, 1, 2, 3, 4]
    shuffled = run_answer_eval.generation_order(43, "shuffle", seed=20261003)
    assert sorted(shuffled) == list(range(43))
    assert shuffled != list(range(43))
    assert shuffled == run_answer_eval.generation_order(43, "shuffle", seed=20261003)


def test_jsonl_round_trip_keeps_unicode(tmp_path):
    path = tmp_path / "runs" / "x.jsonl"
    rows = [{"id": "k1", "answer": "엔드포인트"}, {"id": "k2", "answer": None}]

    write_jsonl(path, rows)

    assert read_jsonl(path) == rows
    assert "엔드포인트" in path.read_text(encoding="utf-8")


# --- rerunning the judge on stored answers --------------------------------------------


async def test_run_judge_rejudges_stored_answers_without_generating(tmp_path, monkeypatch):
    gen_path = tmp_path / "unit.gen.jsonl"
    write_jsonl(gen_path, [gen_record("t2"), gen_record("t1")])
    sent = []

    def handler(request):
        if request.url.path != "/api/chat":  # the run notes /api/version and /api/ps if it can
            return httpx.Response(404, json={"error": "not here"})
        sent.append(json.loads(request.content))
        return chat_response(GOOD_SCORES, prompt_eval_count=2050)

    mock_ollama(monkeypatch, handler)
    out_path = await run_judge.judge_file(
        gen_path,
        JudgeConfig(model="m", num_ctx=None, label="J0"),
        base_url="http://ollama.test",
        count_tokens=lambda messages: 6000,
        order="dataset",
    )

    judgments = read_jsonl(out_path)
    assert out_path.name == "unit.J0.judge.jsonl"
    assert [j["id"] for j in judgments] == ["t1", "t2"]  # dataset order, not file order
    assert all(j["truncation"] == "truncated" for j in judgments)
    assert "num_ctx" not in sent[0]["options"]


# --- comparisons ----------------------------------------------------------------------


def test_paired_bootstrap_is_seeded_and_brackets_the_mean():
    diffs = [1, 0, 0, -1, 2, 0, 1, 0, 0, 1]

    mean, low, high = compare_judgments.paired_bootstrap_ci(diffs)

    assert mean == pytest.approx(0.4)
    assert low <= mean <= high
    assert (mean, low, high) == compare_judgments.paired_bootstrap_ci(diffs)
    assert compare_judgments.paired_bootstrap_ci([0, 0, 0]) == (0.0, 0.0, 0.0)


def test_pairing_counts_ups_downs_and_drops_unscored_items():
    a = [
        {"id": "t1", "correctness_score": 3, "answer_sha1": "x"},
        {"id": "t2", "correctness_score": 5, "answer_sha1": "y"},
        {"id": "t3", "correctness_score": None, "answer_sha1": "z"},
    ]
    b = [
        {"id": "t1", "correctness_score": 5, "answer_sha1": "x"},
        {"id": "t2", "correctness_score": 4, "answer_sha1": "w"},
        {"id": "t3", "correctness_score": 4, "answer_sha1": "z"},
    ]

    paired = compare_judgments.pair_metric(a, b, "correctness_score")

    assert paired.ids == ["t1", "t2"]
    assert paired.diffs == [2, -1]
    assert (paired.up, paired.down, paired.same) == (1, 1, 0)
    assert (paired.sum_a, paired.sum_b) == (8, 9)
    assert compare_judgments.answers_changed(a, b) == 1


def test_pairing_refuses_files_with_different_items():
    with pytest.raises(ValueError, match="t9"):
        compare_judgments.pair_metric(
            [{"id": "t1", "correctness_score": 3}],
            [{"id": "t9", "correctness_score": 3}],
            "correctness_score",
        )

"""The answer eval's judge call, truncation check, per-item records and comparisons.

Until v10 the Ollama judge call set only temperature 0, so it ran in Ollama's default
4096-token context, and Ollama cuts an over-long prompt without saying so. These tests
pin the v11 judge (num_ctx 8192, truncate=false, a pre-flight length check, the
prompt_eval_count kept next to a tokenizer count), the legacy judge kept for comparison,
and the per-item JSONL that lets a judge rerun without regenerating answers. No Ollama,
database or tokenizer download is needed.
"""

# [테스트 묶음] 답변 평가 하네스(eval/judge.py, eval/run_answer_eval.py, eval/run_judge.py,
# eval/compare_judgments.py, eval/tokens.py)의 단위 테스트. 판정 호출 형식, 잘림 탐지, 문항별 기록, 저장된 답
# 재판정, 판정 비교 통계, v13 생성 진단 기록을 고정한다.
# [왜 중요한가] v10까지 판정 호출은 Ollama 기본 문맥(4096)으로 돌았고 Ollama는 긴 프롬프트를 말없이 자른다.
# v11에서 고친 판정(J1)과 옛 판정(J0)을 둘 다 정확히 재현해야 두 결과를 비교할 수 있으므로, 요청 본문을 필드
# 단위로 검사한다(docs/experiments.md v11).
# [방법] 실제 Ollama·DB·토크나이저 없이 돈다. Ollama는 httpx.MockTransport로, 검색은 monkeypatch로,
# 토크나이저는 가짜 클래스로 바꾼다.

import json
import uuid

# httpx: MockTransport로 Ollama HTTP 응답을 흉내 낸다. pytest: 예외 검사(raises)와 근사 비교(approx).
import httpx
import pytest

# 테스트 대상인 평가 모듈들과, 가짜 생성기·검색 결과를 만들 앱의 데이터 클래스를 가져온다.
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

# 판정 스키마에 맞는 정상 점수 한 벌. 여러 테스트가 가짜 판정 응답으로 쓴다.
GOOD_SCORES = {"faithfulness_score": 4, "hallucinated": False, "correctness_score": 5}


# eval/judge.py가 만드는 httpx.AsyncClient를 MockTransport가 붙은 진짜 클라이언트로 바꿔, 네트워크 없이
# handler가 응답을 돌려주게 한다. 다른 인자(timeout 등)는 그대로 넘겨 실제 호출 코드를 바꾸지 않는다.
def mock_ollama(monkeypatch, handler):
    real_client = httpx.AsyncClient
    monkeypatch.setattr(
        judge.httpx,
        "AsyncClient",
        lambda **kwargs: real_client(transport=httpx.MockTransport(handler), **kwargs),
    )


# Ollama /api/chat 성공 응답 모양을 만든다. prompt_eval_count를 바꿔 '잘린 프롬프트'를 흉내 낼 수 있다.
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


# run_answer_eval이 쓰는 gen.jsonl 한 행과 같은 모양의 기록을 만든다. dataset_index는 id의 숫자에서 정해, 정렬
# 순서 테스트에 쓴다. chunks=0이면 검색 결과가 없는 문항이 된다.
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


# J1 판정 요청이 num_ctx 8192와 truncate=false를 보내고, 스키마·메시지·stream 설정이 맞는지 확인한다.
# truncate=false가 빠지면 Ollama가 넘치는 프롬프트를 조용히 잘라 v11에서 고친 점이 사라진다.
def test_v11_judge_asks_for_8192_tokens_and_no_silent_truncation():
    payload = ollama_judge_payload("prompt", JudgeConfig(model="qwen2.5:7b-instruct"))

    assert payload["options"] == {"temperature": 0, "num_ctx": 8192}
    assert payload["truncate"] is False
    assert payload["format"] == JUDGE_SCHEMA
    assert payload["messages"] == [{"role": "user", "content": "prompt"}]
    assert payload["stream"] is False


# J0(num_ctx=None)는 v10까지의 요청과 똑같아야 한다. num_ctx나 truncate 필드가 하나라도 붙으면 옛 판정을
# 재현한 비교(J1 − J0)가 의미를 잃는다.
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


# 판정 프롬프트 문장이 예전과 한 글자도 다르지 않은지 확인한다. 문장이 바뀌면 이전 판정 점수와 비교할 수 없게
# 된다.
def test_judge_prompt_text_is_unchanged():
    prompt = build_judge_prompt("Q?", "ctx", "ans", "ref")

    assert prompt == (
        "Question: Q?\n\n"
        "Context passages the model was given:\nctx\n\n"
        "Model's answer:\nans\n\n"
        "Reference answer:\nref\n\n"
        "Score the model's answer. Both scores use a 1-5 scale, where 1 is worst and 5 is best."
    )


# 판정 결과에 점수뿐 아니라 판정 원문, prompt_eval_count, eval_count, done_reason이 남는지 확인한다.
# prompt_eval_count가 있어야 토크나이저 수와 비교해 잘림을 문항마다 알 수 있다.
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


# 1~5 밖의 점수(9)는 조용히 평균에 섞이지 않고 ValueError로 실패해야 한다.
async def test_judge_still_rejects_scores_off_the_scale(monkeypatch):
    mock_ollama(monkeypatch, lambda request: chat_response({**GOOD_SCORES, "correctness_score": 9}))

    with pytest.raises(ValueError, match="correctness_score=9"):
        await judge_with_ollama("http://ollama.test", "prompt", JudgeConfig(model="m"))


# truncate=false에서 Ollama가 '문맥 초과'로 거절하면 실행을 멈추지 않고 그 문항을 오류로 기록하는지
# 확인한다(점수는 비워 둠). v11 스모크에서 실제로 HTTP 400이 났다.
async def test_context_overflow_error_is_recorded_not_raised(monkeypatch):
    # With truncate=false Ollama refuses an over-long prompt; the item is kept as an error.
    mock_ollama(
        monkeypatch,
        lambda request: httpx.Response(400, json={"error": "the input length exceeds the context length"}),
    )

    outcome = await judge_with_ollama("http://ollama.test", "prompt", JudgeConfig(model="m"))

    assert outcome.correctness_score is None
    assert "exceeds the context length" in outcome.error


# 문맥 초과가 아닌 서버 오류(500)는 기록으로 삼키지 않고 예외로 올라와야 한다. 모든 오류를 삼키면 망가진
# 실행이 정상처럼 끝난다.
async def test_other_ollama_errors_still_raise(monkeypatch):
    mock_ollama(monkeypatch, lambda request: httpx.Response(500, json={"error": "model runner crashed"}))

    with pytest.raises(httpx.HTTPStatusError):
        await judge_with_ollama("http://ollama.test", "prompt", JudgeConfig(model="m"))


# --- truncation detection --------------------------------------------------------------


# 잘림 판정 규칙: prompt_eval_count가 토크나이저 수보다 16토큰 넘게 모자라면 'truncated', 몇 토큰 차이는 'ok',
# 어느 한쪽이 없으면 'unchecked'. 2050은 Ollama 0.35.1이 4096 문맥에서 남기는 길이(앞 4토큰 + 약 절반)를 흉내
# 낸 값이다.
def test_truncation_status_compares_evaluated_and_counted_tokens():
    assert truncation_status(prompt_eval_count=5000, counted_tokens=5003) == "ok"
    # Ollama 0.35.1 keeps 4 tokens plus about half of a 4096 window.
    assert truncation_status(prompt_eval_count=2050, counted_tokens=5003) == "truncated"
    assert truncation_status(prompt_eval_count=None, counted_tokens=5003) == "unchecked"
    assert truncation_status(prompt_eval_count=2050, counted_tokens=None) == "unchecked"


# judge_items가 문항마다 토크나이저 수, 잘림 표시, 판정 설정(라벨 J1, 8192, truncate false), 답 해시, 판정
# 순서를 기록하는지 확인한다. 답 해시는 나중에 '답이 바뀐 문항 수'를 세는 데 쓰인다.
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


# 프롬프트 하나라도 '토큰 수 + 256 > num_ctx'면 JudgeContextError로 멈추고, 판정 호출은 한 번도 나가지 않아야
# 한다. 일부만 판정된 반쪽 결과가 남지 않게 하는 v11 규칙이다.
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


# J0는 길이 확인으로 막지 않고 그대로 보내야 한다. 옛 판정이 얼마나 잘렸는지(M1)를 재는 것이 목적이기
# 때문이다. 기록에는 num_ctx·truncate가 None으로 남는다.
async def test_legacy_judge_items_send_over_long_prompts_to_measure_truncation():
    async def call(prompt):
        return JudgeOutcome(**GOOD_SCORES, prompt_eval_count=2050)

    judgments = await judge_items(
        [gen_record("t1")], JudgeConfig(model="m", num_ctx=None, label="J0"), call, lambda m: 6000
    )

    assert judgments[0]["truncation"] == "truncated"
    assert judgments[0]["judge_num_ctx"] is None
    assert judgments[0]["judge_truncate"] is None


# 검색 결과가 없는 문항은 충실도를 판단할 근거가 없으므로 판정하지 않고 빈 점수와 'unchecked'로 남긴다(v11
# 전과 같은 처리).
async def test_judge_items_skip_questions_without_context():
    async def call(prompt):
        raise AssertionError("no judge call without passages")

    judgments = await judge_items([gen_record("t1", chunks=0)], JudgeConfig(model="m"), call, None)

    assert judgments[0]["correctness_score"] is None
    assert judgments[0]["truncation"] == "unchecked"


# ChatTokenCounter가 채팅 템플릿을 거친 문자열을, 어시스턴트 머리말을 붙이고(add_generation_prompt) 특수
# 토큰을 다시 붙이지 않은 채(add_special_tokens=False) 센다는 것을 가짜 토크나이저로 확인한다.
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


# generate_answer의 기록에 순위별 청크(id, 본문), 첫 정답 순위, 답, 참고 답안, 생성 시간·토큰 수, 키워드
# 커버리지가 들어가는지 확인한다. 마지막 줄은 판정이 보는 컨텍스트가 기록된 본문을 순위대로 이은 것인지 본다.
# 이 기록만으로 생성 없이 다시 판정할 수 있어야 하기 때문이다.
# 검색은 monkeypatch로 고정 결과를 돌려주게 바꿔 DB 없이 돈다.
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



# 두 가지를 확인한다. (1) 정답이 한국어 페이지여도 같은 페이지의 영어 청크가 나오면 맞음으로 센다(페이지 단위
# Hit, v12). (2) --cross-lingual은 한국어 질문에만 적용되고, 바닥값을 주지 않으면 모델의 기본 바닥값(0.3)이
# 검색에 넘어간다.
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

# 생성 순서: dataset이면 그대로, shuffle이면 모든 문항을 한 번씩 담은 다른 순서이고 같은 seed면 항상 같다(v11
# 생성 노이즈 측정을 재현할 수 있게).
def test_generation_order_is_the_dataset_order_or_a_seeded_shuffle():
    assert run_answer_eval.generation_order(5, "dataset", seed=1) == [0, 1, 2, 3, 4]
    shuffled = run_answer_eval.generation_order(43, "shuffle", seed=20261003)
    assert sorted(shuffled) == list(range(43))
    assert shuffled != list(range(43))
    assert shuffled == run_answer_eval.generation_order(43, "shuffle", seed=20261003)


# JSONL 쓰기·읽기가 한글을 이스케이프하지 않고 그대로 저장하고 None도 보존하는지 확인한다. 기록 파일을 사람이
# 직접 읽고 grep할 수 있어야 한다.
def test_jsonl_round_trip_keeps_unicode(tmp_path):
    path = tmp_path / "runs" / "x.jsonl"
    rows = [{"id": "k1", "answer": "엔드포인트"}, {"id": "k2", "answer": None}]

    write_jsonl(path, rows)

    assert read_jsonl(path) == rows
    assert "엔드포인트" in path.read_text(encoding="utf-8")


# --- rerunning the judge on stored answers --------------------------------------------


# run_judge.judge_file이 저장된 답을 생성 없이 판정하고, 파일 순서가 아니라 데이터셋 순서로 판정하며, 출력
# 파일 이름에 라벨(J0)을 넣는지 확인한다. J0라 num_ctx를 보내지 않고, prompt_eval_count(2050) < 토크나이저
# 수(6000)라 모두 'truncated'로 표시된다.
# /api/chat 외의 경로(버전·ps 조회)는 404로 돌려줘도 기록만 비고 실행은 계속된다.
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


# 대응표본 bootstrap 구간: 평균이 정확하고, 구간이 평균을 감싸며, seed가 고정돼 같은 입력이면 같은 구간이
# 나오고, 차이가 모두 0이면 (0, 0, 0)인지 확인한다.
def test_paired_bootstrap_is_seeded_and_brackets_the_mean():
    diffs = [1, 0, 0, -1, 2, 0, 1, 0, 0, 1]

    mean, low, high = compare_judgments.paired_bootstrap_ci(diffs)

    assert mean == pytest.approx(0.4)
    assert low <= mean <= high
    assert (mean, low, high) == compare_judgments.paired_bootstrap_ci(diffs)
    assert compare_judgments.paired_bootstrap_ci([0, 0, 0]) == (0.0, 0.0, 0.0)


# 두 판정 결과를 문항별로 맞출 때 한쪽이라도 점수가 없는 문항은 빼고, 오른·내린 문항 수와 합계, 답이 바뀐 문항
# 수(답 해시 비교)를 맞게 세는지 확인한다.
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


# 문항 구성이 다른 두 파일은 비교하지 않고 다른 문항 id를 담은 ValueError를 내야 한다.
def test_pairing_refuses_files_with_different_items():
    with pytest.raises(ValueError, match="t9"):
        compare_judgments.pair_metric(
            [{"id": "t1", "correctness_score": 3}],
            [{"id": "t9", "correctness_score": 3}],
            "correctness_score",
        )


# --- v13: generation diagnostics and the language guard in the per-item record ----------


# v13 언어 가드가 다시 만든 문항의 기록: 최종 답, 가드 적용 여부, 가드 전 답과 그 답의 가나·한자 섞임, 재시도
# 시간, 호출별 진단(답변 호출 2번, 인용 호출 1번)이 그대로 남는지 확인한다. eval/generator_arms.py가 이
# 기록으로 raw/lg 두 팔을 나누므로 하나라도 빠지면 안 된다.
# 가드 전 답은 v12 n078의 실제 섞임 문장을 본떴다. 한자가 없는 최종 답은 kana_han False가 된다.
async def test_generation_record_keeps_the_guard_and_per_call_diagnostics(monkeypatch):
    chunk = RetrievedChunk(uuid.uuid4(), uuid.uuid4(), "docs/ko/docs/p1.md", "H", "본문", 0.8)
    def call(prompt, output, ms):
        return {
            "prompt_eval_count": prompt,
            "eval_count": output,
            "done_reason": "stop",
            "thinking_chars": 0,
            "ms": ms,
        }

    answer_calls = [call(1800, 371, 5000.0), call(1830, 120, 1500.0)]
    citation_call = call(2200, 12, 400.0)

    async def fake_retrieve(db, question, vector, top_k, mode, **kwargs):
        return [chunk]

    class GuardedGenerator:
        async def answer(self, question, retrieved, language="en"):
            return GenerationResult(
                "`APIRouter`로 나눕니다.",
                [1],
                5830,
                503,
                "local-model",
                diagnostics={
                    "think": False,
                    "guard_applied": True,
                    "unguarded_answer": "APIRouter로 나눕니다. 更好地翻译成中文",
                    "guard_retry_ms": 1500.0,
                    "answer_calls": answer_calls,
                    "citation_call": citation_call,
                    "citation_schema_error": None,
                    "think_tag_in_answer": False,
                },
            )

    class FakeEmbedder:
        model_name = "fake-embedding"

        def embed_query(self, text):
            return [0.0]

    monkeypatch.setattr(run_answer_eval, "retrieve", fake_retrieve)
    q = EvalQuestion("n078", "APIRouter로 나누는 방법?", ["docs/ko/docs/p1.md"], "나눈다.", ["APIRouter"])

    record = await run_answer_eval.generate_answer(
        None, lambda lang: FakeEmbedder(), GuardedGenerator(), q, 5, "dense", None
    )

    assert record["answer"] == "`APIRouter`로 나눕니다."
    assert record["kana_han"] is False
    assert record["guard_applied"] is True
    assert record["unguarded_answer"] == "APIRouter로 나눕니다. 更好地翻译成中文"
    assert record["kana_han_unguarded"] is True
    assert record["guard_retry_ms"] == 1500.0
    assert record["generation_calls"] == {"answer": answer_calls, "citation": citation_call}
    assert record["citation_schema_error"] is None
    assert record["think"] is False and record["think_tag_in_answer"] is False


# 진단을 내지 않는 생성기(Claude, 테스트 가짜)일 때 가드·호출 필드가 False/None으로 채워져 기록 모양이 깨지지
# 않는지 확인한다.
async def test_generation_record_without_diagnostics_keeps_its_old_shape(monkeypatch):
    # The Anthropic provider (and the fakes in other tests) report no diagnostics.
    chunk = RetrievedChunk(uuid.uuid4(), uuid.uuid4(), "docs/en/docs/p1.md", "H", "Text", 0.8)

    async def fake_retrieve(db, question, vector, top_k, mode, **kwargs):
        return [chunk]

    class PlainGenerator:
        async def answer(self, question, retrieved, language="en"):
            return GenerationResult("Use Query().", [1], 900, 40, "claude")

    class FakeEmbedder:
        model_name = "fake-embedding"

        def embed_query(self, text):
            return [0.0]

    monkeypatch.setattr(run_answer_eval, "retrieve", fake_retrieve)
    q = EvalQuestion("t1", "How?", ["docs/en/docs/p1.md"], "Declare it.", ["Query"])

    record = await run_answer_eval.generate_answer(
        None, lambda lang: FakeEmbedder(), PlainGenerator(), q, 5, "dense", None
    )

    assert record["guard_applied"] is False
    assert record["unguarded_answer"] is None
    assert record["generation_calls"] is None


# 평가용 생성기가 strict_citations=False(인용 응답이 깨져도 기록하고 계속)이고, 설정의 think·언어 가드 값을
# 그대로 받는지 확인한다. Settings는 .env를 읽지 않게 _env_file=None으로 만든다.
def test_the_eval_generator_records_bad_citation_replies_instead_of_failing(monkeypatch):
    from app.config import Settings
    from app.services.generation import OllamaGenerationService

    settings = Settings(
        database_url="x", jwt_secret_key="y", _env_file=None, ollama_think=False, language_guard=True
    )

    generator = run_answer_eval.build_generator(settings)

    assert isinstance(generator, OllamaGenerationService)
    assert generator._strict_citations is False
    assert generator._think is False and generator._language_guard is True


# 모델 digest를 /api/tags 목록에서 찾고, 없거나 상태를 못 읽었으면 None을 돌려주는지 확인한다.
def test_model_digest_comes_from_ollama_tags():
    models = [{"name": "a:1", "digest": "aaa"}, {"name": "qwen3.5:9b", "digest": "6488c96f"}]
    state = {"tags": {"models": models}}

    assert run_judge.model_digest(state, "qwen3.5:9b") == "6488c96f"
    assert run_judge.model_digest(state, "missing:1") is None
    assert run_judge.model_digest({}, "qwen3.5:9b") is None


# 토크나이저 설정의 템플릿 인자(qwen3.5의 enable_thinking=False)가 apply_chat_template까지 전달되는지
# 확인한다. 빠지면 템플릿이 그 인자를 반영하지 못해 Ollama가 읽은 프롬프트와 다르게 셀 수 있다.
def test_chat_token_counter_passes_template_arguments():
    seen = {}

    class FakeTokenizer:
        def apply_chat_template(self, messages, tokenize, add_generation_prompt, **kwargs):
            seen.update(kwargs)
            return "x"

        def __call__(self, text, add_special_tokens):
            return {"input_ids": [1]}

    ChatTokenCounter(FakeTokenizer(), {"enable_thinking": False})([{"role": "user", "content": "q"}])

    assert seen == {"enable_thinking": False}


# v13 후보 토크나이저 설정이 문서와 같은지 고정한다: qwen3.5는 thinking 끔, A.X는 gpt2 로더, 모든 리비전은
# 40자 커밋 해시(브랜치 이름이 아니라 고정 리비전).
def test_v13_candidates_have_pinned_tokenizers():
    from eval.tokens import TOKENIZERS

    assert TOKENIZERS["qwen3.5:9b"].template_kwargs == {"enable_thinking": False}
    assert TOKENIZERS["a.x-4.0-light:q4_k_m"].loader == "gpt2"
    assert all(len(spec.revision) == 40 for spec in TOKENIZERS.values())


# 답변 평가 리포트 머리에 모델 digest, think·가드 설정과 재생성 문항 수, done_reason=length 수, 인용 스키마
# 오류 수가 적히는지 확인한다. v13 관문 조건(추론 출력, length, 인용)을 리포트에서 바로 읽을 수 있어야 한다.
def test_report_notes_the_generation_settings_and_diagnostics():
    from eval.answer_report import render_report

    def record(item_id, guard_applied, done_reason, citation_error):
        return {
            "id": item_id,
            "question": "Q",
            "answer": "A",
            "keyword_coverage": 1.0,
            "generation_ms": 1000.0,
            "kana_han": False,
            "guard_applied": guard_applied,
            "generation_calls": {
                "answer": [{"done_reason": done_reason, "thinking_chars": 0}],
                "citation": {"thinking_chars": 0},
            },
            "citation_schema_error": citation_error,
        }

    records = [record("t1", True, "stop", None), record("t2", False, "length", "not JSON")]
    meta = {"model": "qwen3.5:9b", "model_digest": "6488c96f", "think": False, "language_guard": True}

    report = render_report("unit", meta, records, None, None)

    assert "- model digest: 6488c96f" in report
    assert "- think: False, language guard: on (regenerated 1/2)" in report
    assert "done_reason=length: 1/2" in report
    assert "citation replies breaking the schema: 1/2" in report

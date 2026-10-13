"""The Ollama provider's two-call generation, without a running Ollama.

Under schema-constrained decoding the local 7B model didn't escape quotes inside
string values, so answers containing code were cut off at their first `"`. The answer
is therefore generated as free text, and the citations come from a second call
constrained to a digits-only schema. The recorded answer-quality numbers were measured
with this split, so these tests pin it.

v13 (docs/experiments.md) adds an optional think switch for models that reason by
default, an optional language guard for Korean answers that slip into Chinese or
Japanese, and per-call diagnostics the answer eval records. All three are off or inert
by default, so the qwen2.5 payload stays what it was.
"""

# [테스트 묶음] Ollama 생성기(app/services/generation.py의 OllamaGenerationService)의 단위 테스트. 실제 Ollama
# 없이 httpx.MockTransport로 /api/chat 응답을 흉내 내고, 생성기가 보낸 요청 본문을 그대로 검사한다.
# [왜 중요한가] 기록된 답변 품질 수치는 모두 '답변은 자유 텍스트, 인용은 숫자 스키마' 두 단계 호출로 잰
# 것이라, 요청 모양이 바뀌면 이전 측정과 비교할 수 없다(커밋 c5f1f25). v13에서 더한
# think·언어 가드·호출별 진단은 기본값에서 요청을 바꾸지 않아야 하고, 켰을 때는 규칙대로 동작해야
# 한다(docs/experiments.md v13).

import json
import uuid

# httpx: MockTransport로 Ollama 응답을 메모리에서 돌려준다. pytest: 픽스처와 parametrize.
import httpx
import pytest

# 설정 기본값·캐시, 생성 모듈(httpx를 바꿔 끼울 대상과 규칙 문자열), 인용 스키마, 생성기, 검색 결과 데이터
# 클래스를 가져온다.
from app.config import Settings, get_settings
from app.services import generation
from app.services.generation import CITATIONS_SCHEMA, OllamaGenerationService
from app.services.retrieval import RetrievedChunk

# 큰따옴표가 든 코드가 들어간 답. 스키마 제약 디코딩으로 답을 받던 시절 7B가 이런 답을 첫 따옴표에서 잘랐던
# 것이 두 단계 호출로 바꾼 이유다.
ANSWER_WITH_CODE = 'Declare it as `q: str = Query(alias="item-query")`.'


# n번째 가짜 검색 결과(경로·제목·본문만 다름)를 만든다.
def make_chunk(n: int) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=uuid.uuid4(),
        document_id=uuid.uuid4(),
        source_path=f"docs/en/docs/page-{n}.md",
        heading_path=f"Page {n}",
        content=f"Passage {n} text.",
        score=0.5,
    )


# 첫 호출에는 코드가 든 답변을, 두 번째 호출에는 2번 패시지를 인용한 JSON을 돌려주는 가짜 Ollama. 생성기
# 모듈의 httpx.AsyncClient를 바꿔 끼우고, 받은 요청 본문 목록을 돌려준다.
@pytest.fixture
def ollama_requests(monkeypatch):
    """Answer Ollama's /api/chat in memory; returns the request payloads in order."""
    payloads: list[dict] = []

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/chat"
        payloads.append(json.loads(request.content))
        if len(payloads) == 1:
            content = ANSWER_WITH_CODE
        else:
            content = json.dumps({"citations": [{"chunk_number": 2}]})
        return httpx.Response(
            200, json={"message": {"content": content}, "prompt_eval_count": 100, "eval_count": 10}
        )

    real_client = httpx.AsyncClient
    monkeypatch.setattr(
        generation.httpx,
        "AsyncClient",
        lambda **kwargs: real_client(transport=httpx.MockTransport(handler), **kwargs),
    )
    return payloads


# 두 단계 호출을 고정한다: 답변 호출에는 format(스키마)이 없고, 인용 호출에만 CITATIONS_SCHEMA가 붙으며, 인용
# 호출의 마지막 메시지에 답이 그대로 들어간다. 두 호출 모두 num_ctx 8192이고, 토큰 수는 두 호출의 합(100+100,
# 10+10)이다.
@pytest.mark.asyncio
async def test_ollama_answers_in_free_text_then_cites_with_a_schema(ollama_requests):
    service = OllamaGenerationService("http://ollama.test", "local-model")

    result = await service.answer("How do I alias a query parameter?", [make_chunk(1), make_chunk(2)])

    answer_call, citation_call = ollama_requests
    assert "format" not in answer_call
    assert citation_call["format"] == CITATIONS_SCHEMA
    assert ANSWER_WITH_CODE in citation_call["messages"][-1]["content"]
    # Ollama's default 4096-token context is nearly filled by the passages alone.
    assert [call["options"]["num_ctx"] for call in ollama_requests] == [8192, 8192]

    assert result.answer == ANSWER_WITH_CODE
    assert result.cited_chunk_numbers == [2]
    assert (result.input_tokens, result.output_tokens) == (200, 20)


# --- v13: think switch, language guard, per-call diagnostics ---------------------------

# v13 테스트용 고정 문장: 한국어 질문, 설명 글에 중국어가 섞인 답(가드가 걸려야 함), 깨끗한 한국어 답, 2번을
# 인용하는 인용 응답.
KOREAN_Q = "쿼리 매개변수에 별칭을 주려면?"
MIXED_KO = "별칭은 `Query(alias=...)`로 줍니다. 이렇게 하면 代码更好地翻译。"
CLEAN_KO = "별칭은 `Query(alias=...)`로 줍니다."
CITE_2 = (json.dumps({"citations": [{"chunk_number": 2}]}), {})


# 호출 순서대로 미리 적어 둔 (내용, 추가 필드) 응답을 돌려주는 가짜 Ollama. 추가 필드로 thinking,
# prompt_eval_count, eval_count, done_reason을 바꿔 진단 기록을 검사할 수 있다. 테스트가 script에 응답을 채워
# 넣는다.
@pytest.fixture
def scripted_ollama(monkeypatch):
    """Answer each /api/chat call from a script of (content, extra fields).

    Returns the request payloads and the script list, which the test fills in.
    """
    payloads: list[dict] = []
    script: list[tuple[str, dict]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        payloads.append(json.loads(request.content))
        content, extra = script[len(payloads) - 1]
        message = {"role": "assistant", "content": content}
        if "thinking" in extra:
            message["thinking"] = extra["thinking"]
        body = {
            "message": message,
            "prompt_eval_count": extra.get("prompt_eval_count", 100),
            "eval_count": extra.get("eval_count", 10),
            "done_reason": extra.get("done_reason", "stop"),
        }
        return httpx.Response(200, json=body)

    real_client = httpx.AsyncClient
    monkeypatch.setattr(
        generation.httpx,
        "AsyncClient",
        lambda **kwargs: real_client(transport=httpx.MockTransport(handler), **kwargs),
    )
    return payloads, script


# 기본 설정(think 없음, 가드 꺼짐)에서는 요청에 think 필드가 없고, 필드 구성과 options가 v12까지와 정확히
# 같아야 한다. qwen2.5 기준 실행의 요청이 바뀌면 이전 측정과 비교할 수 없다.
@pytest.mark.asyncio
async def test_the_default_payload_has_no_think_field(scripted_ollama):
    # The qwen2.5 baseline must keep sending exactly what it sent through v12.
    payloads, script = scripted_ollama
    script += [(CLEAN_KO, {}), CITE_2]

    await OllamaGenerationService("http://ollama.test", "m").answer(
        KOREAN_Q, [make_chunk(1), make_chunk(2)], "ko"
    )

    assert all("think" not in p for p in payloads)
    assert set(payloads[0]) == {"model", "messages", "stream", "options"}
    assert payloads[0]["options"] == {"temperature": 0, "num_ctx": 8192, "num_predict": 1024}


# think=False를 주면 답변·인용 두 호출 모두에 보낸다(qwen3.5처럼 기본으로 추론하는 모델의 추론을 끄려고).
@pytest.mark.asyncio
async def test_think_false_is_sent_on_both_calls(scripted_ollama):
    payloads, script = scripted_ollama
    script += [(CLEAN_KO, {}), CITE_2]

    service = OllamaGenerationService("http://ollama.test", "qwen3.5:9b", think=False)
    await service.answer(KOREAN_Q, [make_chunk(1), make_chunk(2)], "ko")

    assert [p["think"] for p in payloads] == [False, False]


# 언어 가드: 한국어 답의 설명 글에 한자가 있으면, 한국어 규칙을 KOREAN_RETRY_RULE로 바꾼 같은 요청(같은
# 패시지·질문, 스키마 없음)을 한 번 더 보낸다. 인용은 최종 답에 대해 받고, 진단에 가드 적용·가드 전 답·두 답변
# 호출의 토큰 수·재시도 시간이 남으며, 출력 토큰은 세 호출의 합이다.
@pytest.mark.asyncio
async def test_language_guard_regenerates_a_mixed_korean_answer_once(scripted_ollama):
    payloads, script = scripted_ollama
    script += [(MIXED_KO, {"eval_count": 371}), (CLEAN_KO, {"eval_count": 120}), CITE_2]

    service = OllamaGenerationService("http://ollama.test", "m", language_guard=True)
    result = await service.answer(KOREAN_Q, [make_chunk(1), make_chunk(2)], "ko")

    first, retry, citation = payloads
    assert first["messages"][0]["content"] == generation.system_prompt_for(
        generation.OLLAMA_ANSWER_PROMPT, "ko"
    )
    assert generation.KOREAN_RETRY_RULE in retry["messages"][0]["content"]
    assert generation.KOREAN_ANSWER_RULE not in retry["messages"][0]["content"]
    assert retry["messages"][1] == first["messages"][1]  # same passages and question
    assert "format" not in retry
    assert CLEAN_KO in citation["messages"][-1]["content"]  # citations for the final answer

    assert result.answer == CLEAN_KO
    assert result.cited_chunk_numbers == [2]
    d = result.diagnostics
    assert d["guard_applied"] is True
    assert d["unguarded_answer"] == MIXED_KO
    assert [c["eval_count"] for c in d["answer_calls"]] == [371, 120]
    assert d["guard_retry_ms"] >= 0
    assert result.output_tokens == 371 + 120 + 10


# 다시 만든 답에도 섞여 있어도 더 보내지 않는다(호출 3번: 답변, 재시도, 인용). 가드는 한 번만 재시도하는
# 규칙이다.
@pytest.mark.asyncio
async def test_language_guard_retries_only_once(scripted_ollama):
    payloads, script = scripted_ollama
    script += [(MIXED_KO, {}), (MIXED_KO + " 再", {}), CITE_2]

    service = OllamaGenerationService("http://ollama.test", "m", language_guard=True)
    result = await service.answer(KOREAN_Q, [make_chunk(1), make_chunk(2)], "ko")

    assert len(payloads) == 3
    assert result.answer == MIXED_KO + " 再"
    assert result.diagnostics["guard_applied"] is True


# 가드가 걸리면 안 되는 경우: 한자가 코드 블록이나 인라인 코드 안에만 있는 답, 영어 질문, 가드를 켜지 않은
# 경우. 모두 호출이 두 번(답변, 인용)뿐이고 가드 전 답 기록이 없어야 한다.
@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("question", "language", "answer", "guard"),
    [
        (KOREAN_Q, "ko", "코드 예:\n```python\n# 设置\nx = 1\n```\n끝.", True),  # Han inside a fence
        (KOREAN_Q, "ko", "`変数`라는 이름은 코드에만 있습니다.", True),  # Han inside inline code
        ("How do I alias a query?", "en", "Use alias. 代码", True),  # English questions are left alone
        (KOREAN_Q, "ko", MIXED_KO, False),  # the guard is off unless asked for
    ],
)
async def test_language_guard_leaves_other_answers_alone(
    scripted_ollama, question, language, answer, guard
):
    payloads, script = scripted_ollama
    script += [(answer, {}), CITE_2]

    service = OllamaGenerationService("http://ollama.test", "m", language_guard=guard)
    result = await service.answer(question, [make_chunk(1), make_chunk(2)], language)

    assert len(payloads) == 2
    assert result.answer == answer
    assert result.diagnostics["guard_applied"] is False
    assert "unguarded_answer" not in result.diagnostics


# 재시도 판정 함수만 따로 검사한다: 한국어 설명 글의 한자·가나는 걸리고, 닫힌·닫히지 않은 코드 블록과 인라인
# 코드 안의 한자, 영어 질문의 답은 걸리지 않는다. 닫히지 않은 코드 블록은 답 끝까지 코드로 본다.
def test_needs_language_retry_looks_at_korean_prose_only():
    assert generation.needs_language_retry("한국어 답입니다. 中文", "ko")
    assert generation.needs_language_retry("ひらがなが混ざった답", "ko")
    assert not generation.needs_language_retry("한국어 답입니다.", "ko")
    assert not generation.needs_language_retry("```\n中文\n```", "ko")
    assert not generation.needs_language_retry("```python\n中文 (fence never closed)", "ko")
    assert not generation.needs_language_retry("한국어 `中文` 답", "ko")
    assert not generation.needs_language_retry("English 中文", "en")


# 호출별 진단 기록: done_reason(length면 1024토큰에서 잘림), 실제 읽은 프롬프트 토큰 수, 추론 출력 길이, 시간,
# 답 안의 <think> 태그 여부. 인용 번호 9는 패시지 수(2)를 넘지만 스키마는 정수만 요구하므로 스키마 오류가
# 아니다(범위는 보고만 하는 지표).
@pytest.mark.asyncio
async def test_diagnostics_keep_done_reason_thinking_and_citation_validity(scripted_ollama):
    payloads, script = scripted_ollama
    script += [
        (
            "<think>hmm</think>답",
            {"done_reason": "length", "thinking": "reasoning", "prompt_eval_count": 2222},
        ),
        (json.dumps({"citations": [{"chunk_number": 9}]}), {"prompt_eval_count": 2400}),
    ]

    service = OllamaGenerationService("http://ollama.test", "m", think=False)
    result = await service.answer(KOREAN_Q, [make_chunk(1), make_chunk(2)], "ko")

    d = result.diagnostics
    assert d["think"] is False
    assert d["answer_calls"][0]["done_reason"] == "length"
    assert d["answer_calls"][0]["prompt_eval_count"] == 2222
    assert d["answer_calls"][0]["thinking_chars"] == len("reasoning")
    assert d["answer_calls"][0]["ms"] >= 0
    assert d["think_tag_in_answer"] is True
    assert d["citation_call"]["prompt_eval_count"] == 2400
    assert d["citation_schema_error"] is None  # 9 is out of range, but the schema holds
    assert "citation_reply" not in d
    assert result.cited_chunk_numbers == [9]


# 평가 모드(strict_citations=False)에서는 스키마를 어긴 인용 응답(JSON 아님, 빈 목록, 문자열 번호, 다른 키)을
# 예외 없이 오류 문구와 원문으로 기록한다. JSON이 아니면 인용 번호는 빈 목록이다. v13이 인용 스키마 오류 수를
# 세려고 넣은 동작이다.
@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("reply", "error"),
    [
        ("not json", "not JSON"),
        (json.dumps({"citations": []}), "empty"),
        (json.dumps({"citations": [{"chunk_number": "2"}]}), "integer"),
        (json.dumps({"cited": [1]}), "citations"),
    ],
)
async def test_lenient_citations_record_a_reply_that_breaks_the_schema(scripted_ollama, reply, error):
    payloads, script = scripted_ollama
    script += [(CLEAN_KO, {}), (reply, {})]

    service = OllamaGenerationService("http://ollama.test", "m", strict_citations=False)
    result = await service.answer(KOREAN_Q, [make_chunk(1), make_chunk(2)], "ko")

    assert error in result.diagnostics["citation_schema_error"]
    assert result.diagnostics["citation_reply"] == reply
    if reply == "not json":
        assert result.cited_chunk_numbers == []


# 앱 기본(strict)에서는 인용 응답이 JSON이 아니면 예전처럼 실패해야 한다. 평가용 완화가 앱 동작을 바꾸지
# 않았는지 확인한다.
@pytest.mark.asyncio
async def test_the_app_still_fails_on_a_citation_reply_that_is_not_json(scripted_ollama):
    payloads, script = scripted_ollama
    script += [(CLEAN_KO, {}), ("not json", {})]

    with pytest.raises(json.JSONDecodeError):
        await OllamaGenerationService("http://ollama.test", "m").answer(KOREAN_Q, [make_chunk(1)], "ko")


# 앱의 생성기 팩토리가 환경 변수 OLLAMA_THINK·LANGUAGE_GUARD를 설정을 거쳐 생성기에 넘기는지 확인한다. 설정과
# 생성기는 lru_cache로 캐시되므로 앞뒤로 캐시를 비워, 이 테스트의 환경 변수가 다른 테스트에 남지 않게 한다.
def test_the_service_takes_think_and_the_guard_from_settings(monkeypatch):
    monkeypatch.setenv("OLLAMA_THINK", "false")
    monkeypatch.setenv("LANGUAGE_GUARD", "true")
    monkeypatch.setenv("GENERATION_PROVIDER", "ollama")
    get_settings.cache_clear()
    generation.get_generation_service.cache_clear()
    try:
        service = generation.get_generation_service()
        assert service._think is False
        assert service._language_guard is True
    finally:
        get_settings.cache_clear()
        generation.get_generation_service.cache_clear()


# 코드의 기본값이 v13 채택 결과(생성 모델 A.X-4.0-Light, think 보내지 않음, 언어 가드 켬)인지 고정한다. 환경
# 변수와 .env를 지워 코드 기본값만 본다.
def test_the_defaults_are_the_v13_adoption(monkeypatch):
    monkeypatch.delenv("OLLAMA_MODEL_NAME", raising=False)
    monkeypatch.delenv("OLLAMA_THINK", raising=False)
    monkeypatch.delenv("LANGUAGE_GUARD", raising=False)
    settings = Settings(database_url="x", jwt_secret_key="y", _env_file=None)

    assert settings.ollama_model_name == "a.x-4.0-light:q4_k_m"
    assert settings.ollama_think is None
    assert settings.language_guard is True

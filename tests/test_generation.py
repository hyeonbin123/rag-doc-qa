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

import json
import uuid

import httpx
import pytest

from app.config import Settings, get_settings
from app.services import generation
from app.services.generation import CITATIONS_SCHEMA, OllamaGenerationService
from app.services.retrieval import RetrievedChunk

ANSWER_WITH_CODE = 'Declare it as `q: str = Query(alias="item-query")`.'


def make_chunk(n: int) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=uuid.uuid4(),
        document_id=uuid.uuid4(),
        source_path=f"docs/en/docs/page-{n}.md",
        heading_path=f"Page {n}",
        content=f"Passage {n} text.",
        score=0.5,
    )


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

KOREAN_Q = "쿼리 매개변수에 별칭을 주려면?"
MIXED_KO = "별칭은 `Query(alias=...)`로 줍니다. 이렇게 하면 代码更好地翻译。"
CLEAN_KO = "별칭은 `Query(alias=...)`로 줍니다."
CITE_2 = (json.dumps({"citations": [{"chunk_number": 2}]}), {})


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


@pytest.mark.asyncio
async def test_think_false_is_sent_on_both_calls(scripted_ollama):
    payloads, script = scripted_ollama
    script += [(CLEAN_KO, {}), CITE_2]

    service = OllamaGenerationService("http://ollama.test", "qwen3.5:9b", think=False)
    await service.answer(KOREAN_Q, [make_chunk(1), make_chunk(2)], "ko")

    assert [p["think"] for p in payloads] == [False, False]


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


@pytest.mark.asyncio
async def test_language_guard_retries_only_once(scripted_ollama):
    payloads, script = scripted_ollama
    script += [(MIXED_KO, {}), (MIXED_KO + " 再", {}), CITE_2]

    service = OllamaGenerationService("http://ollama.test", "m", language_guard=True)
    result = await service.answer(KOREAN_Q, [make_chunk(1), make_chunk(2)], "ko")

    assert len(payloads) == 3
    assert result.answer == MIXED_KO + " 再"
    assert result.diagnostics["guard_applied"] is True


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


def test_needs_language_retry_looks_at_korean_prose_only():
    assert generation.needs_language_retry("한국어 답입니다. 中文", "ko")
    assert generation.needs_language_retry("ひらがなが混ざった답", "ko")
    assert not generation.needs_language_retry("한국어 답입니다.", "ko")
    assert not generation.needs_language_retry("```\n中文\n```", "ko")
    assert not generation.needs_language_retry("```python\n中文 (fence never closed)", "ko")
    assert not generation.needs_language_retry("한국어 `中文` 답", "ko")
    assert not generation.needs_language_retry("English 中文", "en")


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


@pytest.mark.asyncio
async def test_the_app_still_fails_on_a_citation_reply_that_is_not_json(scripted_ollama):
    payloads, script = scripted_ollama
    script += [(CLEAN_KO, {}), ("not json", {})]

    with pytest.raises(json.JSONDecodeError):
        await OllamaGenerationService("http://ollama.test", "m").answer(KOREAN_Q, [make_chunk(1)], "ko")


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


def test_the_defaults_are_the_v13_adoption(monkeypatch):
    monkeypatch.delenv("OLLAMA_MODEL_NAME", raising=False)
    monkeypatch.delenv("OLLAMA_THINK", raising=False)
    monkeypatch.delenv("LANGUAGE_GUARD", raising=False)
    settings = Settings(database_url="x", jwt_secret_key="y", _env_file=None)

    assert settings.ollama_model_name == "a.x-4.0-light:q4_k_m"
    assert settings.ollama_think is None
    assert settings.language_guard is True

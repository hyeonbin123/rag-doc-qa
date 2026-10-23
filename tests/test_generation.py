"""실행 중인 Ollama 없이, Ollama 제공자의 두 단계 호출 생성을 검증한다.

스키마 제약 디코딩에서 로컬 7B 모델은 문자열 값 안의 따옴표를 이스케이프하지 못해, 코드가 든 답이 첫
`"`에서 잘렸다. 그래서 답은 자유 텍스트로 생성하고, 인용은 숫자만 담는 스키마로 제약한 두 번째 호출에서
받는다. 기록된 답변 품질 수치는 이렇게 나눈 상태로 쟀으므로, 이 테스트들이 그 구조를 고정한다.

v13(docs/experiments.md)은 기본으로 추론하는 모델을 위한 선택적 think 스위치, 중국어나 일본어로 새는 한국어
답을 위한 선택적 언어 가드, 답변 평가가 기록하는 호출별 진단을 더했다. 셋 다 기본값에서는 꺼져 있거나
아무 영향이 없으므로, qwen2.5에 보내는 요청 본문은 예전 그대로다.
"""

# [테스트 묶음] Ollama 생성기(app/services/generation.py의 OllamaGenerationService)의 단위 테스트. 실제 Ollama
# 없이 httpx.MockTransport로 /api/chat 응답을 흉내 내고, 생성기가 보낸 요청 본문을 그대로 검사한다.
# [왜 중요한가] 기록된 답변 품질 수치는 모두 '답변은 자유 텍스트, 인용은 숫자 스키마' 두 단계 호출로 잰
# 것이라, 요청 모양이 바뀌면 이전 측정과 비교할 수 없다(커밋 c5f1f25). v13에서 더한
# think·언어 가드·호출별 진단은 기본값에서 요청을 바꾸지 않아야 하고, 켰을 때는 규칙대로 동작해야
# 한다(docs/experiments.md v13).

import json
import ssl
import uuid

# anthropic: Claude 경로의 SDK 예외 클래스(장애 코드 변환 테스트). httpx2: anthropic SDK가 쓰는 HTTP
# 라이브러리로, SDK 예외를 만들 때 필요한 Request·Response 객체를 만든다. httpx: MockTransport로 Ollama
# 응답을 메모리에서 돌려준다. pytest: 픽스처와 parametrize.
import anthropic
import httpx
import httpx2
import pytest

# 설정 기본값·캐시, 생성 모듈(httpx를 바꿔 끼울 대상과 규칙 문자열), 인용 스키마, 생성기, 검색 결과 데이터
# 클래스, 판정 호출(eval/judge.py)과 Ollama 상태 읽기(eval/run_judge.py)를 가져온다.
from app.config import Settings, get_settings
from app.services import generation
from app.services.generation import CITATIONS_SCHEMA, OllamaGenerationService
from app.services.retrieval import RetrievedChunk
from eval import judge, run_judge

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
    """Ollama의 /api/chat에 메모리에서 답한다. 받은 요청 본문을 순서대로 돌려준다."""
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
    # Ollama 기본 문맥 4096토큰은 문단만으로도 거의 찬다.
    assert [call["options"]["num_ctx"] for call in ollama_requests] == [8192, 8192]

    assert result.answer == ANSWER_WITH_CODE
    assert result.cited_chunk_numbers == [2]
    assert (result.input_tokens, result.output_tokens) == (200, 20)


# --- v13: think 스위치, 언어 가드, 호출별 진단 ---

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
    """/api/chat 호출마다 (내용, 추가 필드) 각본에서 응답을 꺼내 답한다.

    받은 요청 본문 목록과, 테스트가 채워 넣을 각본 목록을 돌려준다.
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
    # qwen2.5 기준선은 v12까지 보내던 요청을 그대로 보내야 한다.
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
    assert retry["messages"][1] == first["messages"][1]  # 같은 문단과 질문
    assert "format" not in retry
    assert CLEAN_KO in citation["messages"][-1]["content"]  # 인용은 최종 답 기준

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
        (KOREAN_Q, "ko", "코드 예:\n```python\n# 设置\nx = 1\n```\n끝.", True),  # 펜스 안의 한자
        (KOREAN_Q, "ko", "`変数`라는 이름은 코드에만 있습니다.", True),  # 인라인 코드 안의 한자
        ("How do I alias a query?", "en", "Use alias. 代码", True),  # 영어 질문은 건드리지 않는다
        (KOREAN_Q, "ko", MIXED_KO, False),  # 켜라고 하지 않으면 가드는 꺼져 있다
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
    assert d["citation_schema_error"] is None  # 9는 범위 밖이지만 스키마는 지킨다
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


# --- v15 후보: 인용 호출을 답변 대화에 이어 붙이기, 청크 0개 거절, 거절 답의 인용 비우기 ---
# (docs/experiments.md v15. 셋 다 설정으로만 켜지고 기본값에서는 요청·응답이 전과 같다.)

# 짧은 숫자 배열 스키마로 받는 인용 응답(이어 붙이기 모드).
COMPACT_CITE_2 = (json.dumps({"citations": [2]}), {})


# 이어 붙이기 모드: 인용 호출은 답변 호출의 메시지(같은 system, 같은 user) 뒤에 모델이 쓴 답(assistant)과 짧은
# 질문(user)을 붙인 대화이고, 출력은 정수 배열 스키마다. 앞부분이 답변 호출과 같아야 Ollama가 프롬프트 캐시를
# 다시 쓴다.
@pytest.mark.asyncio
async def test_followup_citations_continue_the_answer_conversation(scripted_ollama):
    payloads, script = scripted_ollama
    raw_answer = CLEAN_KO + "\n"  # 모델이 보낸 그대로(끝 줄바꿈 포함)를 assistant 메시지로 되돌려 준다
    script += [(raw_answer, {}), COMPACT_CITE_2]

    service = OllamaGenerationService("http://ollama.test", "m", citation_mode="followup")
    result = await service.answer(KOREAN_Q, [make_chunk(1), make_chunk(2)], "ko")

    answer_call, citation_call = payloads
    assert citation_call["messages"][:2] == answer_call["messages"]
    assert citation_call["messages"][2] == {"role": "assistant", "content": raw_answer}
    assert citation_call["messages"][3] == {
        "role": "user",
        "content": generation.CITATION_FOLLOWUP_PROMPT,
    }
    assert citation_call["format"] == generation.COMPACT_CITATIONS_SCHEMA
    assert citation_call["options"] == answer_call["options"]
    assert result.answer == CLEAN_KO
    assert result.cited_chunk_numbers == [2]
    assert result.diagnostics["citation_mode"] == "followup"
    assert result.diagnostics["citation_schema_error"] is None


# 이어 붙이기 모드에서 언어 가드가 다시 만들었으면, 인용 호출은 '다시 만든 요청'(KOREAN_RETRY_RULE system)과
# 다시 만든 답을 잇는다.
@pytest.mark.asyncio
async def test_followup_citations_continue_the_guarded_retry(scripted_ollama):
    payloads, script = scripted_ollama
    script += [(MIXED_KO, {}), (CLEAN_KO, {}), COMPACT_CITE_2]

    service = OllamaGenerationService(
        "http://ollama.test", "m", language_guard=True, citation_mode="followup"
    )
    result = await service.answer(KOREAN_Q, [make_chunk(1), make_chunk(2)], "ko")

    _, retry, citation = payloads
    assert citation["messages"][:2] == retry["messages"]
    assert citation["messages"][2]["content"] == CLEAN_KO
    assert result.cited_chunk_numbers == [2]


# 짧은 스키마를 어긴 응답(빈 배열, 예전 객체 모양, 정수가 아닌 값)은 평가 모드에서 이유와 함께 기록한다.
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "reply, error",
    [
        ('{"citations": []}', "empty citations array"),
        ('{"citations": [{"chunk_number": 2}]}', "is not an integer"),
        ('{"citations": [true]}', "is not an integer"),
    ],
)
async def test_followup_citation_schema_errors_are_recorded(scripted_ollama, reply, error):
    payloads, script = scripted_ollama
    script += [(CLEAN_KO, {}), (reply, {})]

    service = OllamaGenerationService(
        "http://ollama.test", "m", citation_mode="followup", strict_citations=False
    )
    result = await service.answer(KOREAN_Q, [make_chunk(1), make_chunk(2)], "ko")

    assert error in result.diagnostics["citation_schema_error"]
    assert result.cited_chunk_numbers == []


# 청크 0개 거절을 켜면 검색 결과가 없을 때 LLM을 부르지 않고 언어별 고정 거절문을 돌려준다. 인용은 비고,
# 그 거절문은 거절 분류기에도 거절로 잡힌다.
@pytest.mark.asyncio
@pytest.mark.parametrize("language", ["en", "ko"])
async def test_no_chunks_returns_the_fixed_refusal_without_calling_the_llm(scripted_ollama, language):
    payloads, script = scripted_ollama

    service = OllamaGenerationService("http://ollama.test", "m", refuse_without_context=True)
    result = await service.answer("anything", [], language)

    assert payloads == []
    assert result.answer == generation.NO_CONTEXT_REFUSAL[language]
    assert result.cited_chunk_numbers == []
    assert result.diagnostics["refused_without_context"] is True
    assert generation.is_refusal_answer(result.answer, language)


# 기본값에서는 청크가 0개여도 예전처럼 LLM을 부른다(지금 바닥값 0.3에서는 청크 0개가 생기지 않는다).
@pytest.mark.asyncio
async def test_by_default_no_chunks_still_calls_the_llm(scripted_ollama):
    payloads, script = scripted_ollama
    script += [("I don't know.", {}), CITE_2]

    await OllamaGenerationService("http://ollama.test", "m").answer("anything", [], "en")

    assert len(payloads) == 2


# 거절 답의 인용 비우기를 켜면, 거절로 분류된 답은 인용 호출을 하지 않고 인용 없이 돌려준다. 거절이 아닌 답은
# 그대로 두 호출이다.
@pytest.mark.asyncio
async def test_a_refusal_answer_gets_no_citation_call_when_enabled(scripted_ollama):
    payloads, script = scripted_ollama
    script += [("I don't know. The passages do not cover this.", {})]

    service = OllamaGenerationService("http://ollama.test", "m", empty_citations_on_refusal=True)
    result = await service.answer("Q?", [make_chunk(1)], "en")

    assert len(payloads) == 1
    assert result.cited_chunk_numbers == []
    assert result.diagnostics["citation_skipped"] == "refusal"
    assert result.diagnostics["citation_call"] is None


@pytest.mark.asyncio
async def test_a_normal_answer_is_still_cited_when_refusal_emptying_is_on(scripted_ollama):
    payloads, script = scripted_ollama
    script += [(CLEAN_KO, {}), CITE_2]

    service = OllamaGenerationService("http://ollama.test", "m", empty_citations_on_refusal=True)
    result = await service.answer(KOREAN_Q, [make_chunk(1), make_chunk(2)], "ko")

    assert len(payloads) == 2
    assert result.cited_chunk_numbers == [2]


# 거절 분류기는 답의 첫 문장만 본다. '문서에 정보가 없다'로 시작하는 답은 거절이고, 첫 문장에서 답한 뒤
# 뒤쪽에서 일부만 모른다고 한 답이나, '할 수 없습니다'가 답의 내용인 경우는 거절이 아니다(저장된 답에서 본
# 모양들).
@pytest.mark.parametrize(
    "answer, language, expected",
    [
        ("I don't know.", "en", True),
        ("I don't know. The passages discuss routers.", "en", True),
        ("The provided context passages do not contain information about status codes.", "en", True),
        ("Based on the provided context passages, there is no information explaining it.", "en", True),
        ("This is not covered in the provided passages.", "en", True),
        # 2026-10-18 보강: v15 I4 dev 답에서 놓쳤던 거절 꼴
        # (A.X의 "You don't know", 한국어 '제공되지/제공하지 않')
        ("You don't know how to tune it based on the provided context passages.", "en", True),
        ("죄송하지만, 그 방법에 대한 정보는 제공되지 않았습니다.", "ko", True),
        ("죄송하지만, 주어진 문맥에서는 그 방법에 대한 정보를 제공하지 않습니다.", "ko", True),
        ("Poetry의 설정을 바꾸는 방법은 문서에서 제공되지 않습니다.", "ko", True),
        ("Use `Query(alias=...)`. The docs do not mention other options.", "en", False),
        ("You cannot send JSON and files together; use Form fields.", "en", False),
        ("모르겠습니다. 찾은 문서 구절에는 이 질문에 대한 내용이 없습니다.", "ko", True),
        ("제공된 문맥에는 deprecated 매개변수에 대한 정보가 포함되어 있지 않습니다.", "ko", True),
        ("주어진 문서에 해당 내용이 없습니다.", "ko", True),
        ("죄송하지만, 주어진 문맥에서는 그 방법에 대한 정보가 없습니다.", "ko", True),
        ("제공된 문서에서는 이 질문에 답할 수 없습니다.", "ko", True),
        (
            "아니요, 파일과 JSON 본문을 함께 받을 수 없습니다. 요청이 multipart로 인코딩되기 때문입니다.",
            "ko",
            False,
        ),
        ("`--workers` 옵션으로 여러 워커를 띄울 수 있습니다. gunicorn에 대한 정보는 없습니다.", "ko", False),
    ],
)
def test_is_refusal_answer_reads_the_first_sentence(answer, language, expected):
    assert generation.is_refusal_answer(answer, language) is expected


# 세 설정이 환경 변수 → 설정 → 생성기로 넘어간다. 기본값은 v15 결정대로: 인용 호출은 separate(I3 채택 안 함),
# 청크 0개 거절은 꺼짐(I4 바닥값과 함께 채택 안 함), 거절 답의 인용 비우기는 켜짐(I4에서 채택,
# docs/experiments.md v15).
def test_the_v15_switches_come_from_settings_with_the_v15_defaults(monkeypatch):
    for name in ("CITATION_MODE", "REFUSE_WITHOUT_CONTEXT", "EMPTY_CITATIONS_ON_REFUSAL"):
        monkeypatch.delenv(name, raising=False)
    settings = Settings(database_url="x", jwt_secret_key="y", _env_file=None)
    assert settings.citation_mode == "separate"
    assert settings.refuse_without_context is False
    assert settings.empty_citations_on_refusal is True

    monkeypatch.setenv("CITATION_MODE", "followup")
    monkeypatch.setenv("REFUSE_WITHOUT_CONTEXT", "true")
    monkeypatch.setenv("EMPTY_CITATIONS_ON_REFUSAL", "true")
    monkeypatch.setenv("GENERATION_PROVIDER", "ollama")
    get_settings.cache_clear()
    generation.get_generation_service.cache_clear()
    try:
        service = generation.get_generation_service()
        assert service._citation_mode == "followup"
        assert service._refuse_without_context is True
        assert service._empty_citations_on_refusal is True
    finally:
        get_settings.cache_clear()
        generation.get_generation_service.cache_clear()


# --- 생성기 호출 경로: 인증서 번들은 한 번만 읽기, 장애를 코드로 알리기, 요청 본문 고정 ---
# httpx는 클라이언트를 만들 때마다(정확히는 기본 transport를 만들 때마다) 기본 SSL 컨텍스트를 만들면서 certifi
# CA 번들을 동기로 읽는다. Ollama 주소는 http라 그 컨텍스트는 쓰이지도 않는데, Windows 호스트에서는 호출당 CPU
# 약 0.3초가 들고 그동안 이벤트 루프가 멈췄다. 위 픽스처들은 AsyncClient에 MockTransport를 넣어 기본 transport
# 생성을 건너뛰므로 이 비용이 보이지 않았다. 그래서 아래 테스트는 실제 클라이언트·transport 생성 경로를 그대로
# 두고, 요청을 보내는 단계(AsyncHTTPTransport.handle_async_request)만 가짜로 바꾼다.


# ssl.SSLContext.load_verify_locations(CA 번들 파일 읽기) 호출을 센다. 실제 읽기는 그대로 한다.
@pytest.fixture
def ca_bundle_loads(monkeypatch):
    """CA 번들 읽기 호출의 인자를 순서대로 모은 목록을 돌려준다."""
    loads: list[tuple] = []
    real_load = ssl.SSLContext.load_verify_locations

    def counting_load(self, *args, **kwargs):
        loads.append(args)
        return real_load(self, *args, **kwargs)

    monkeypatch.setattr(ssl.SSLContext, "load_verify_locations", counting_load)
    return loads


# 실제 AsyncClient·AsyncHTTPTransport는 그대로 만들고, 네트워크로 보내는 단계만 reply(request)의 응답(또는
# reply가 낸 httpx 예외)으로 바꾼다. 보낸 요청 목록을 돌려준다.
def fake_network(monkeypatch, reply) -> list[httpx.Request]:
    sent: list[httpx.Request] = []

    async def handle_async_request(self, request):
        sent.append(request)
        return reply(request)

    monkeypatch.setattr(httpx.AsyncHTTPTransport, "handle_async_request", handle_async_request)
    return sent


# Ollama /api/chat 성공 응답. format(스키마)이 붙은 호출이면 1번 문단 인용 JSON, 아니면 답 글을 돌려준다.
def answer_then_citation(request: httpx.Request) -> httpx.Response:
    body = json.loads(request.content)
    content = json.dumps({"citations": [{"chunk_number": 1}]}) if "format" in body else "Use a path."
    return httpx.Response(
        200, json={"message": {"content": content}, "prompt_eval_count": 7, "eval_count": 3}
    )


# 질문 두 개(답변·인용 호출 4번)를 해도 CA 번들은 많아야 한 번 읽는다(프로세스 첫 호출에서 공유 SSL 컨텍스트를
# 만들 때). 고치기 전에는 호출마다 한 번씩, 4번 읽었다.
@pytest.mark.asyncio
async def test_ollama_calls_read_the_ca_bundle_at_most_once(monkeypatch, ca_bundle_loads):
    sent = fake_network(monkeypatch, answer_then_citation)
    service = OllamaGenerationService("http://ollama.test", "m")

    for _ in range(2):
        result = await service.answer("How do I declare a path parameter?", [make_chunk(1)], "en")

    assert len(sent) == 4
    assert result.cited_chunk_numbers == [1]
    assert len(ca_bundle_loads) <= 1


# 판정 호출(eval/judge.py의 judge_with_ollama)과 캐시 되돌리기 요청(flush_ollama)도 같은 공유 SSL 컨텍스트를
# 쓴다. 판정 450회짜리 실행이면 호출마다 읽는 비용이 몇 분이 된다.
@pytest.mark.asyncio
async def test_judge_and_flush_calls_read_the_ca_bundle_at_most_once(monkeypatch, ca_bundle_loads):
    scores = {"faithfulness_score": 4, "hallucinated": False, "correctness_score": 5}

    def reply(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        content = json.dumps(scores) if "format" in body else "2"
        return httpx.Response(
            200, json={"message": {"content": content}, "prompt_eval_count": 5, "eval_count": 1}
        )

    sent = fake_network(monkeypatch, reply)
    config = judge.JudgeConfig(model="m")

    for _ in range(2):
        await judge.flush_ollama("http://ollama.test", config)
        outcome = await judge.judge_with_ollama("http://ollama.test", "prompt", config)

    assert len(sent) == 4
    assert outcome.correctness_score == 5
    assert len(ca_bundle_loads) <= 1


# 실행 조건 기록용 Ollama 상태 읽기(eval/run_judge.py의 ollama_state, 실행당 1~2번)도 같은 컨텍스트를 쓴다.
@pytest.mark.asyncio
async def test_ollama_state_reads_the_ca_bundle_at_most_once(monkeypatch, ca_bundle_loads):
    sent = fake_network(monkeypatch, lambda request: httpx.Response(200, json={"models": []}))

    for _ in range(2):
        state = await run_judge.ollama_state("http://ollama.test")

    assert len(sent) == 6  # version, ps, tags를 두 번
    assert state["tags"] == {"models": []}
    assert len(ca_bundle_loads) <= 1


# 공유 컨텍스트는 프로세스에 하나이고, 인증서 검증을 끄지 않는다(verify=False가 아님). OLLAMA_BASE_URL을
# https로 둔 배포에서도 서버 인증서와 호스트 이름을 검사해야 한다.
def test_the_shared_ssl_context_is_one_object_that_still_verifies():
    context = generation.ollama_ssl_context()

    assert context is generation.ollama_ssl_context()
    assert context.verify_mode == ssl.CERT_REQUIRED
    assert context.check_hostname is True


# 요청을 보내는 단계에서 httpx 예외를 내는 reply를 만든다(연결 거부, 읽기 시간 초과 흉내).
def raising(exc_type: type[httpx.TransportError]):
    def reply(request: httpx.Request) -> httpx.Response:
        raise exc_type("simulated by the test", request=request)

    return reply


# Ollama 장애는 GenerationUnavailableError와 code로 올라온다: 연결 실패·5xx는 generator_unavailable, 시간
# 초과는 generator_timeout, 모델 태그가 없을 때의 404는 generator_model_missing. /query/ask는 이것을 503으로
# 바꾼다(app/main.py). 원래 httpx 예외는 __cause__로 남아 로그에서 볼 수 있고, Ollama가 보낸 오류 본문은
# 응답이 아니라 로그에만 쓰도록 upstream에 담긴다.
@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("reply", "code", "upstream_part"),
    [
        (raising(httpx.ConnectError), "generator_unavailable", "ConnectError"),  # Ollama가 꺼져 있음
        (raising(httpx.ReadTimeout), "generator_timeout", "ReadTimeout"),  # 제한 시간 안에 답이 없음
        (
            lambda request: httpx.Response(404, json={"error": "model 'm' not found"}),
            "generator_model_missing",
            "model 'm' not found",
        ),
        (
            lambda request: httpx.Response(500, json={"error": "llama runner process has terminated"}),
            "generator_unavailable",
            "llama runner process has terminated",
        ),
    ],
)
async def test_ollama_outages_become_unavailable_errors_with_a_code(monkeypatch, reply, code, upstream_part):
    fake_network(monkeypatch, reply)

    with pytest.raises(generation.GenerationUnavailableError) as caught:
        await OllamaGenerationService("http://ollama.test", "m").answer("Q?", [make_chunk(1)], "en")

    assert caught.value.code == code
    assert caught.value.retry_after > 0
    assert caught.value.message
    assert upstream_part in caught.value.upstream
    assert isinstance(caught.value.__cause__, httpx.HTTPError)


# 404가 아닌 4xx(예: 요청 본문이나 think 설정을 Ollama가 거부)는 생성기 장애가 아니라 이쪽 요청의 문제라,
# 503으로 바꾸지 않고 원래 예외를 그대로 올린다(500과 트레이스백으로 드러나게).
@pytest.mark.asyncio
async def test_a_request_ollama_rejects_is_not_reported_as_an_outage(monkeypatch):
    fake_network(monkeypatch, lambda request: httpx.Response(400, json={"error": "invalid format"}))

    with pytest.raises(httpx.HTTPStatusError):
        await OllamaGenerationService("http://ollama.test", "m").answer("Q?", [make_chunk(1)], "en")


# 기본 설정(think 없음)의 두 요청 본문을 필드 단위로 고정한다. 공유 SSL 컨텍스트와 장애 처리는 요청을 보내는
# 방법만 바꾸므로, 기록된 정확도·인용 수치를 낸 요청과 같아야 한다.
@pytest.mark.asyncio
async def test_the_request_bodies_stay_as_they_were_measured(scripted_ollama):
    payloads, script = scripted_ollama
    script += [("Use `Path()`.", {}), CITE_2]

    await OllamaGenerationService("http://ollama.test", "a.x-4.0-light:q4_k_m").answer(
        "How do I declare a path parameter?", [make_chunk(1), make_chunk(2)], "en"
    )

    options = {"temperature": 0, "num_ctx": 8192, "num_predict": 1024}
    context = "[1] (Page 1)\nPassage 1 text.\n\n[2] (Page 2)\nPassage 2 text."
    answer_system = (
        "You are a documentation assistant answering questions about FastAPI using ONLY the "
        "numbered context passages provided below. Rules:\n"
        "1. Answer only using information present in the context passages.\n"
        "2. If the passages do not contain enough information to answer, say you don't know "
        "instead of guessing.\n"
        "3. Reply with the answer text only — no JSON, no preamble.\n"
    )
    citation_system = (
        "Given a question, numbered context passages, and an answer that was written from them, "
        "report which passages the answer actually relied on. Return their [N] numbers."
    )
    assert payloads == [
        {
            "model": "a.x-4.0-light:q4_k_m",
            "messages": [
                {"role": "system", "content": answer_system},
                {
                    "role": "user",
                    "content": f"Context passages:\n\n{context}\n\n"
                    "Question: How do I declare a path parameter?",
                },
            ],
            "stream": False,
            "options": options,
        },
        {
            "model": "a.x-4.0-light:q4_k_m",
            "messages": [
                {"role": "system", "content": citation_system},
                {
                    "role": "user",
                    "content": "Question: How do I declare a path parameter?\n\n"
                    f"Context passages:\n\n{context}\n\n"
                    "Answer that was written:\nUse `Path()`.",
                },
            ],
            "stream": False,
            "options": options,
            "format": CITATIONS_SCHEMA,
        },
    ]


# Claude 경로의 SDK 예외를 만드는 도우미. 상태 코드 예외는 그 코드의 응답 객체가 있어야 만들어진다.
ANTHROPIC_REQUEST = httpx2.Request("POST", "https://api.anthropic.com/v1/messages")


def anthropic_status_error(cls: type[anthropic.APIStatusError], status: int) -> anthropic.APIStatusError:
    return cls(
        f"Error code: {status}", response=httpx2.Response(status, request=ANTHROPIC_REQUEST), body=None
    )


# messages.create가 정해 둔 예외를 내는 가짜 Claude 클라이언트. 실제 API는 부르지 않는다.
class RaisingMessages:
    def __init__(self, exc: Exception) -> None:
        self.exc = exc

    async def create(self, **kwargs):
        raise self.exc


class RaisingAnthropicClient:
    def __init__(self, exc: Exception) -> None:
        self.messages = RaisingMessages(exc)


def claude_service_raising(exc: Exception) -> generation.AnthropicGenerationService:
    service = generation.AnthropicGenerationService("test-key", "claude-test")
    service._client = RaisingAnthropicClient(exc)
    return service


# Claude 경로도 같은 코드로 바꾼다: 연결 실패·5xx·529(과부하)는 generator_unavailable, 시간 초과는
# generator_timeout, 404(모델 이름 없음)는 generator_model_missing. SDK는 이런 오류를 스스로 몇 번 다시 시도한
# 뒤에 예외를 낸다.
@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("exc", "code"),
    [
        (anthropic.APIConnectionError(request=ANTHROPIC_REQUEST), "generator_unavailable"),
        (anthropic.APITimeoutError(request=ANTHROPIC_REQUEST), "generator_timeout"),
        (anthropic_status_error(anthropic.InternalServerError, 500), "generator_unavailable"),
        (anthropic_status_error(anthropic.OverloadedError, 529), "generator_unavailable"),
        (anthropic_status_error(anthropic.NotFoundError, 404), "generator_model_missing"),
    ],
)
async def test_claude_outages_become_unavailable_errors_with_a_code(exc, code):
    with pytest.raises(generation.GenerationUnavailableError) as caught:
        await claude_service_raising(exc).answer("Q?", [make_chunk(1)], "en")

    assert caught.value.code == code
    assert caught.value.__cause__ is exc


# 그 밖의 Claude 오류(400 잘못된 요청, 401 키 오류, 429 한도 초과 등)는 장애로 숨기지 않고 그대로 올린다.
# 우리 요청이나 설정의 문제를 503 뒤에 감추지 않으려는 것이다.
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "exc",
    [
        anthropic_status_error(anthropic.BadRequestError, 400),
        anthropic_status_error(anthropic.AuthenticationError, 401),
        anthropic_status_error(anthropic.RateLimitError, 429),
    ],
)
async def test_claude_request_errors_are_not_reported_as_outages(exc):
    with pytest.raises(type(exc)):
        await claude_service_raising(exc).answer("Q?", [make_chunk(1)], "en")

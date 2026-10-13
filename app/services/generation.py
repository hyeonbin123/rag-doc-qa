"""Answer generation with structured, schema-enforced citations.

Two interchangeable providers behind one interface:
- Anthropic: forces the `cite_answer` tool via `tool_choice`.
- Ollama: forces the same JSON schema via Ollama's `format` (constrained decoding).

Both guarantee schema-valid citations without parsing free-form text, so
`/query/ask` never has to care which one is wired in.
"""

# [파일 역할] 검색된 청크를 근거로 LLM 답변과 인용(근거 청크 번호)을 만드는 생성 단계. 로컬 Ollama와 Claude
# API 두 제공자를 같은 인터페이스(GenerationService.answer) 뒤에 둔다.
# [설계 이유]
# - 인용을 자유 텍스트에서 파싱하지 않고 JSON 스키마로 강제한다(README '인용을 스키마로 강제'). Claude는
#   tool_choice로 도구 호출을, Ollama는 format(제약 디코딩)으로 스키마를 따르게 한다.
# - Ollama 경로만 호출을 두 번으로 나눈다. 로컬 7B 모델이 제약 디코딩 중 문자열 안의 따옴표를 이스케이프하지
#   못해 코드가 든 답이 잘렸기 때문에, 답변은 자유 텍스트로 받고 인용(숫자 목록)만 따로 스키마로 받는다.
# - 한국어 질문에만 한국어 답변 규칙을 붙이고, 한국어 답에 한자·가나가 섞이면 한 번 다시 만드는 언어 가드를
#   둔다(v8, v13).
# [연결] /query/ask(app/routers/query.py)가 get_generation_service 결과를 의존성으로 받아 answer를 부른다.
# 평가(eval/run_answer_eval.py)도 같은 생성기를 strict_citations=False로 만들어 쓰고, 프롬프트 상수를 가져다
# 토큰 수를 센다.

from __future__ import annotations

import json
import re
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from functools import lru_cache

# httpx: Ollama REST API(/api/chat)를 비동기로 부른다. AsyncAnthropic: Claude Messages API 비동기 클라이언트.
# RetrievedChunk: 검색 결과 청크(본문·헤딩)를 프롬프트로 만들 때 쓴다.
import httpx
from anthropic import AsyncAnthropic

from app.config import get_settings
from app.services.language import Language
from app.services.retrieval import RetrievedChunk

# 두 제공자가 공유하는 기본 지시: 주어진 번호 붙은 문맥만 근거로 답하고, 근거가 부족하면 추측하지 말고
# 모른다고 하라. 환각을 줄이려는 RAG의 기본 규칙이다. 영어 프롬프트 문장은 테스트로 고정돼 있다(v8에서
# 프롬프트 한 줄 때문에 영어 정확도가 떨어진 일이 있었다).
BASE_RULES = (
    "You are a documentation assistant answering questions about FastAPI using ONLY the "
    "numbered context passages provided below. Rules:\n"
    "1. Answer only using information present in the context passages.\n"
    "2. If the passages do not contain enough information to answer, say you don't know "
    "instead of guessing.\n"
)

# Claude용: cite_answer 도구를 반드시 호출하고 citations에 실제로 쓴 청크 번호를 넣으라는 규칙을 더한다.
ANTHROPIC_SYSTEM_PROMPT = BASE_RULES + (
    "3. Always call the cite_answer tool. In `citations`, list the chunk_number of every "
    "passage you actually relied on to construct the answer.\n"
)

# Ollama 답변 호출용: JSON이나 머리말 없이 답 글만 쓰라는 규칙을 더한다(인용은 다음 호출에서 따로 받는다).
OLLAMA_ANSWER_PROMPT = BASE_RULES + (
    "3. Reply with the answer text only — no JSON, no preamble.\n"
)

# Added only for Korean questions. A general "answer in the question's language" rule
# (that mentioned Korean as the example) made the local 7B model answer English
# questions in Korean too, dropping English answer correctness from 4.60 to 4.19.
KOREAN_ANSWER_RULE = (
    "4. Write the answer in Korean. Keep code, API names and identifiers exactly as they "
    "appear in the passages.\n"
)


# 한국어 질문이면 기본 프롬프트 뒤에 한국어 답변 규칙을 붙이고, 영어면 원래 프롬프트를 그대로 쓴다.
def system_prompt_for(prompt: str, language: Language) -> str:
    return prompt + KOREAN_ANSWER_RULE if language == "ko" else prompt


# The language guard (docs/experiments.md v13; on by default since the v13 adoption through
# Settings.language_guard, LANGUAGE_GUARD=false turns it off): a Korean
# answer with kana or Han characters outside code is generated once more with this rule in
# place of KOREAN_ANSWER_RULE. The docs never use those scripts, so in an answer they mean
# the model slipped into Japanese or Chinese (v10-v12 saw it in the 7B model's answers).
KOREAN_RETRY_RULE = (
    "4. Write the entire answer in Korean only (한국어로만 답하세요). Do not switch to Chinese "
    "or Japanese: no Chinese characters and no Japanese kana outside code. Keep code, API "
    "names and identifiers exactly as they appear in the passages.\n"
)

# 가나(U+3040~U+30FF)와 한자(U+4E00~U+9FFF) 범위. 평가 스크립트(eval/run_answer_eval.py,
# eval/generator_arms.py)도 섞인 답을 셀 때 이 정규식을 가져다 쓴다.
# _FENCED_CODE_RE·_INLINE_CODE_RE: 펜스 코드 블록과 인라인 코드. 코드 안의 한자(예: 예제 문자열)는 언어 섞임이
# 아니므로 가드 판단에서 뺀다.
KANA_HAN_RE = re.compile(r"[぀-ヿ一-鿿]")
# A fence that is never closed runs to the end of the answer.
_FENCED_CODE_RE = re.compile(r"```.*?(?:```|\Z)", re.DOTALL)
_INLINE_CODE_RE = re.compile(r"`[^`\n]*`")


# 답에서 코드 부분을 공백으로 바꿔 지우고 설명 글만 남긴다. 펜스 블록을 먼저 지운 뒤 인라인 코드를 지운다.
def prose_outside_code(text: str) -> str:
    return _INLINE_CODE_RE.sub(" ", _FENCED_CODE_RE.sub(" ", text))


# 한국어 질문의 답에서 코드 밖에 가나·한자가 하나라도 있으면 다시 만들어야 한다고 본다. 영어 질문에는 언제나
# False.
def needs_language_retry(answer: str, language: Language) -> bool:
    return language == "ko" and bool(KANA_HAN_RE.search(prose_outside_code(answer)))

# Ollama 두 번째 호출(인용 추출)용 지시: 질문·번호 붙은 문맥·이미 쓴 답을 보고 답이 실제로 기댄 [N] 번호를
# 돌려준다.
OLLAMA_CITATION_PROMPT = (
    "Given a question, numbered context passages, and an answer that was written from them, "
    "report which passages the answer actually relied on. Return their [N] numbers."
)

# 인용 호출의 출력 스키마: chunk_number 정수를 담은 객체 배열, 최소 1개. Ollama format에 넘겨 제약 디코딩으로
# 이 모양만 나오게 한다. 숫자만 있으므로 따옴표 이스케이프 문제가 생기지 않는다.
CITATIONS_SCHEMA = {
    "type": "object",
    "properties": {
        "citations": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "properties": {"chunk_number": {"type": "integer"}},
                "required": ["chunk_number"],
            },
        }
    },
    "required": ["citations"],
}


# 인용 응답이 스키마를 어기는 이유를 문자열로 돌려준다(맞으면 None). bool은 파이썬에서 int의 하위 타입이라
# 따로 걸러 낸다. 앱 동작에는 영향이 없고, 평가가 스키마를 지킨 응답 수를 세는 데 쓴다(eval/answer_report.py).
def citation_schema_error(reply: str) -> str | None:
    """Why a citation reply breaks CITATIONS_SCHEMA, or None when it fits.

    Only recorded (the answer eval counts schema-valid replies); the app parses the reply
    as it always has.
    """
    try:
        parsed = json.loads(reply)
    except ValueError:
        return "not JSON"
    if not isinstance(parsed, dict) or not isinstance(parsed.get("citations"), list):
        return "no citations array"
    if not parsed["citations"]:
        return "empty citations array"
    for item in parsed["citations"]:
        number = item.get("chunk_number") if isinstance(item, dict) else None
        if not isinstance(number, int) or isinstance(number, bool):
            return "chunk_number is not an integer"
    return None


# Claude 도구 입력 스키마: 답 글(answer)과 인용 배열(citations)을 한 번에 받는다.
ANSWER_SCHEMA = {
    "type": "object",
    "properties": {
        "answer": {"type": "string", "description": "The answer to the user's question."},
        "citations": {
            "type": "array",
            # minItems forces schema-constrained decoding to emit at least one citation;
            # smaller local models otherwise satisfy the schema with an empty array.
            "minItems": 1,
            "items": {
                "type": "object",
                "properties": {
                    "chunk_number": {
                        "type": "integer",
                        "description": "The [N] label of a context passage that was used.",
                    }
                },
                "required": ["chunk_number"],
            },
        },
    },
    "required": ["answer", "citations"],
}

# Claude에게 주는 도구 정의. tool_choice로 이 도구를 강제하면 응답이 항상 ANSWER_SCHEMA 모양의 도구 입력으로
# 온다.
CITE_ANSWER_TOOL = {
    "name": "cite_answer",
    "description": "Return the answer to the user's question along with the passages used.",
    "input_schema": ANSWER_SCHEMA,
}


# 생성 결과. answer는 답 글, cited_chunk_numbers는 1부터 시작하는 [N] 번호 목록, 토큰 수와 모델 이름은 질문
# 기록(query_logs)에 저장된다.
@dataclass
class GenerationResult:
    answer: str
    cited_chunk_numbers: list[int]
    input_tokens: int
    output_tokens: int
    model_name: str
    # Provider-specific details the answer eval records (per-call token counts, stop
    # reasons, the language guard); the app does not read them.
    diagnostics: dict = field(default_factory=dict)


# 검색된 청크를 '[번호] (헤딩 경로)' + 본문 형태로 이어 붙인 문맥 블록. 번호는 1부터이고, 모델이 돌려준 인용
# 번호를 다시 청크로 바꿀 때 이 순서를 쓴다.
def _build_context_block(chunks: list[RetrievedChunk]) -> str:
    parts = []
    for i, chunk in enumerate(chunks, start=1):
        heading = chunk.heading_path or "(no heading)"
        parts.append(f"[{i}] ({heading})\n{chunk.content}")
    return "\n\n".join(parts)


# 사용자 메시지: 문맥 블록을 먼저, 질문을 마지막에 둔다.
def _build_user_message(question: str, chunks: list[RetrievedChunk]) -> str:
    return f"Context passages:\n\n{_build_context_block(chunks)}\n\nQuestion: {question}"


# 생성기 공통 인터페이스. 라우터는 이 타입만 알고, 어느 제공자인지는 설정이 정한다. 테스트는 이것을 상속한
# 가짜 생성기를 끼운다(tests/conftest.py).
class GenerationService(ABC):
    @abstractmethod
    async def answer(
        self, question: str, chunks: list[RetrievedChunk], language: Language = "en"
    ) -> GenerationResult: ...


# Claude API 생성기. 한 번의 호출로 답과 인용을 함께 받는다. README에 적힌 대로 코드와 단위 테스트만 있고 실제
# API로는 돌려 보지 않았다(크레딧 없음).
class AnthropicGenerationService(GenerationService):
    def __init__(self, api_key: str, model_name: str) -> None:
        self._client = AsyncAnthropic(api_key=api_key)
        self._model_name = model_name

    async def answer(
        self, question: str, chunks: list[RetrievedChunk], language: Language = "en"
    ) -> GenerationResult:
        # tool_choice로 cite_answer 도구를 강제해, 모델이 자유 텍스트 대신 스키마에 맞는 도구 입력을 내게
        # 한다. 출력은 최대 1024토큰.
        response = await self._client.messages.create(
            model=self._model_name,
            max_tokens=1024,
            system=system_prompt_for(ANTHROPIC_SYSTEM_PROMPT, language),
            tools=[CITE_ANSWER_TOOL],
            tool_choice={"type": "tool", "name": "cite_answer"},
            messages=[{"role": "user", "content": _build_user_message(question, chunks)}],
        )

        # 응답 내용 중 도구 호출 블록을 찾아 그 입력(answer, citations)을 꺼낸다.
        tool_use_block = next(block for block in response.content if block.type == "tool_use")
        tool_input = tool_use_block.input

        return GenerationResult(
            answer=tool_input["answer"],
            cited_chunk_numbers=[c["chunk_number"] for c in tool_input.get("citations", [])],
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            model_name=self._model_name,
        )


class OllamaGenerationService(GenerationService):
    """Local generation, split into two calls.

    A 7B model under JSON-schema-constrained decoding does not reliably escape
    quotes inside string values, so an answer containing code gets truncated at
    its first `"`. Generating the prose free-form and extracting citations in a
    second, digits-only schema call sidesteps that entirely.

    Options added for v13 (docs/experiments.md), all inert by default:
    - `think`: sent as Ollama's `think` field when set (False turns off the reasoning
      that models such as qwen3.5 do by default); None sends no field.
    - `language_guard`: a Korean answer with kana or Han outside code is generated once
      more with KOREAN_RETRY_RULE; the citations are taken for the final answer.
    - `strict_citations=False` (the answer eval) records a citation reply that breaks
      the schema instead of raising, so a run can count them.
    """

    # CONTEXT_TOKENS: 요청마다 num_ctx로 문맥 크기를 8192로 지정한다. MAX_OUTPUT_TOKENS: 답 길이
    # 상한(num_predict 1024). 문맥 8192 중 1024는 답에 쓰이는 셈이다(docs/experiments.md v11의 계산).
    # Ollama defaults to a 4096-token context, which the retrieved passages alone can
    # nearly fill — leaving no room for the answer.
    CONTEXT_TOKENS = 8192
    MAX_OUTPUT_TOKENS = 1024

    # base_url: Ollama 서버 주소, model_name: Ollama 모델 태그, timeout: 한 호출의 제한 시간(초, 기본 180).
    # 나머지 세 옵션은 위 docstring 참고. 앱은 설정의 think·language_guard를 넘기고, 평가는
    # strict_citations=False를 더한다.
    def __init__(
        self,
        base_url: str,
        model_name: str,
        timeout: float = 180.0,
        *,
        think: bool | None = None,
        language_guard: bool = False,
        strict_citations: bool = True,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._model_name = model_name
        self._timeout = timeout
        self._think = think
        self._language_guard = language_guard
        self._strict_citations = strict_citations

    # Ollama /api/chat를 한 번 부른다(스트리밍 없이 완성된 응답 하나).
    # - temperature 0: 같은 입력에 최대한 같은 답이 나오게 해 평가를 반복할 수 있게 한다(docs/experiments.md
    #   v13에 따르면 그래도 실행마다 완전히 같지는 않았다).
    # - response_schema가 있으면 format으로 넘겨 제약 디코딩을 켠다(인용 호출만).
    # - think는 설정됐을 때만 보낸다. 값이 없으면 v13 이전과 똑같은 요청이 된다.
    # 호출마다 새 AsyncClient를 연다. HTTP 오류는 raise_for_status로 예외가 된다.
    async def _chat(self, messages: list[dict], response_schema: dict | None) -> dict:
        payload = {
            "model": self._model_name,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": 0,
                "num_ctx": self.CONTEXT_TOKENS,
                "num_predict": self.MAX_OUTPUT_TOKENS,
            },
        }
        if response_schema is not None:
            payload["format"] = response_schema
        if self._think is not None:
            payload["think"] = self._think

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.post(f"{self._base_url}/api/chat", json=payload)
            response.raise_for_status()
            return response.json()

    # _chat에 호출별 진단을 더한다: 실제로 읽은 프롬프트 토큰 수(prompt_eval_count), 출력 토큰 수(eval_count),
    # 끝난 이유(done_reason, length면 1024토큰에서 잘린 것), 추론 출력 길이, 걸린 시간(ms). 앱은 쓰지 않고
    # 평가가 문항별로 기록한다.
    async def _timed_chat(self, messages: list[dict], response_schema: dict | None) -> tuple[dict, dict]:
        start = time.perf_counter()
        data = await self._chat(messages, response_schema)
        message = data.get("message") or {}
        stats = {
            "prompt_eval_count": data.get("prompt_eval_count"),
            "eval_count": data.get("eval_count"),
            "done_reason": data.get("done_reason"),
            "thinking_chars": len(message.get("thinking") or ""),
            "ms": (time.perf_counter() - start) * 1000,
        }
        return data, stats

    # 답변 호출 메시지: 시스템 메시지(규칙) + 사용자 메시지(문맥 + 질문).
    def _answer_messages(self, question: str, chunks: list[RetrievedChunk], rule_set: str) -> list[dict]:
        return [
            {"role": "system", "content": rule_set},
            {"role": "user", "content": _build_user_message(question, chunks)},
        ]

    async def answer(
        self, question: str, chunks: list[RetrievedChunk], language: Language = "en"
    ) -> GenerationResult:
        context_block = _build_context_block(chunks)

        # 1) 답변 호출: 스키마 없이 자유 텍스트로 받는다. 그래서 코드 속 따옴표가 있어도 잘리지 않는다.
        answer_data, answer_stats = await self._timed_chat(
            self._answer_messages(question, chunks, system_prompt_for(OLLAMA_ANSWER_PROMPT, language)),
            response_schema=None,
        )
        answer_text = answer_data["message"]["content"].strip()
        answer_calls = [answer_stats]
        replies = [answer_data]
        diagnostics: dict = {"think": self._think, "guard_applied": False}

        # 2) 언어 가드(설정 LANGUAGE_GUARD, v13 채택 뒤 기본 켬): 한국어 답의 설명 글에 한자·가나가 있으면
        #    한국어 규칙을 더 강하게 쓴 KOREAN_RETRY_RULE로 한 번만 다시 만든다. 다시 만든 답을 최종 답으로
        #    쓰고, 가드 전 답과 재시도 시간은 진단에 남긴다. v13 채택 측정에서 A.X-4.0-Light는 한국어 155문항
        #    동안 가드가 한 번도 걸리지 않았다(docs/experiments.md v13).
        if self._language_guard and needs_language_retry(answer_text, language):
            retry_data, retry_stats = await self._timed_chat(
                self._answer_messages(question, chunks, OLLAMA_ANSWER_PROMPT + KOREAN_RETRY_RULE),
                response_schema=None,
            )
            diagnostics.update(
                guard_applied=True, unguarded_answer=answer_text, guard_retry_ms=retry_stats["ms"]
            )
            answer_text = retry_data["message"]["content"].strip()
            answer_calls.append(retry_stats)
            replies.append(retry_data)

        # 3) 인용 호출: 최종 답과 같은 문맥을 다시 보여 주고, 답이 기댄 청크 번호만 CITATIONS_SCHEMA로 받는다.
        citation_data, citation_stats = await self._timed_chat(
            [
                {"role": "system", "content": OLLAMA_CITATION_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"Question: {question}\n\n"
                        f"Context passages:\n\n{context_block}\n\n"
                        f"Answer that was written:\n{answer_text}"
                    ),
                },
            ],
            response_schema=CITATIONS_SCHEMA,
        )
        # 인용 응답 파싱. 스키마 위반 이유는 기록용으로 먼저 계산해 둔다. 앱(strict_citations=True)은 JSON이
        # 깨졌으면 예외를 그대로 올리고, 평가는 빈 인용으로 계속 진행한다.
        reply = citation_data["message"]["content"]
        schema_error = citation_schema_error(reply)
        try:
            parsed = json.loads(reply)
            cited = [c["chunk_number"] for c in parsed.get("citations", [])]
        except (ValueError, KeyError, TypeError, AttributeError):
            if self._strict_citations:
                raise
            cited = []

        # 평가가 볼 진단: 호출별 통계, 스키마 위반 이유, 답에 추론 태그(think 태그)가 새어 나왔는지. 스키마를
        # 어긴 경우에만 원래 인용 응답을 함께 남긴다.
        diagnostics.update(
            answer_calls=answer_calls,
            citation_call=citation_stats,
            citation_schema_error=schema_error,
            think_tag_in_answer=any(
                "<think>" in r["message"]["content"] or "</think>" in r["message"]["content"]
                for r in replies
            ),
        )
        if schema_error is not None:
            diagnostics["citation_reply"] = reply

        # 토큰 수는 이 질문에 쓴 모든 호출(답변, 가드 재시도, 인용)의 합이다. 값이 없는 응답은 0으로 센다.
        calls = [*replies, citation_data]
        return GenerationResult(
            answer=answer_text,
            cited_chunk_numbers=cited,
            input_tokens=sum(c.get("prompt_eval_count", 0) for c in calls),
            output_tokens=sum(c.get("eval_count", 0) for c in calls),
            model_name=self._model_name,
            diagnostics=diagnostics,
        )


# 설정에 맞는 생성기를 프로세스당 하나 만든다. GENERATION_PROVIDER=ollama(기본)면 Ollama 생성기에
# 모델·think·언어 가드 설정을 넘기고, 아니면 Claude 생성기를 만든다. app/dependencies.py의 get_generator가
# 이것을 돌려준다.
@lru_cache
def get_generation_service() -> GenerationService:
    settings = get_settings()
    if settings.generation_provider == "ollama":
        return OllamaGenerationService(
            settings.ollama_base_url,
            settings.ollama_model_name,
            think=settings.ollama_think,
            language_guard=settings.language_guard,
        )
    return AnthropicGenerationService(settings.anthropic_api_key, settings.claude_model_name)

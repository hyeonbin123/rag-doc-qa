"""Answer generation with structured, schema-enforced citations.

Two interchangeable providers behind one interface:
- Anthropic: forces the `cite_answer` tool via `tool_choice`.
- Ollama: forces the same JSON schema via Ollama's `format` (constrained decoding).

Both guarantee schema-valid citations without parsing free-form text, so
`/query/ask` never has to care which one is wired in.
"""

from __future__ import annotations

import json
import re
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from functools import lru_cache

import httpx
from anthropic import AsyncAnthropic

from app.config import get_settings
from app.services.language import Language
from app.services.retrieval import RetrievedChunk

BASE_RULES = (
    "You are a documentation assistant answering questions about FastAPI using ONLY the "
    "numbered context passages provided below. Rules:\n"
    "1. Answer only using information present in the context passages.\n"
    "2. If the passages do not contain enough information to answer, say you don't know "
    "instead of guessing.\n"
)

ANTHROPIC_SYSTEM_PROMPT = BASE_RULES + (
    "3. Always call the cite_answer tool. In `citations`, list the chunk_number of every "
    "passage you actually relied on to construct the answer.\n"
)

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

KANA_HAN_RE = re.compile(r"[぀-ヿ一-鿿]")
# A fence that is never closed runs to the end of the answer.
_FENCED_CODE_RE = re.compile(r"```.*?(?:```|\Z)", re.DOTALL)
_INLINE_CODE_RE = re.compile(r"`[^`\n]*`")


def prose_outside_code(text: str) -> str:
    return _INLINE_CODE_RE.sub(" ", _FENCED_CODE_RE.sub(" ", text))


def needs_language_retry(answer: str, language: Language) -> bool:
    return language == "ko" and bool(KANA_HAN_RE.search(prose_outside_code(answer)))

OLLAMA_CITATION_PROMPT = (
    "Given a question, numbered context passages, and an answer that was written from them, "
    "report which passages the answer actually relied on. Return their [N] numbers."
)

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

CITE_ANSWER_TOOL = {
    "name": "cite_answer",
    "description": "Return the answer to the user's question along with the passages used.",
    "input_schema": ANSWER_SCHEMA,
}


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


def _build_context_block(chunks: list[RetrievedChunk]) -> str:
    parts = []
    for i, chunk in enumerate(chunks, start=1):
        heading = chunk.heading_path or "(no heading)"
        parts.append(f"[{i}] ({heading})\n{chunk.content}")
    return "\n\n".join(parts)


def _build_user_message(question: str, chunks: list[RetrievedChunk]) -> str:
    return f"Context passages:\n\n{_build_context_block(chunks)}\n\nQuestion: {question}"


class GenerationService(ABC):
    @abstractmethod
    async def answer(
        self, question: str, chunks: list[RetrievedChunk], language: Language = "en"
    ) -> GenerationResult: ...


class AnthropicGenerationService(GenerationService):
    def __init__(self, api_key: str, model_name: str) -> None:
        self._client = AsyncAnthropic(api_key=api_key)
        self._model_name = model_name

    async def answer(
        self, question: str, chunks: list[RetrievedChunk], language: Language = "en"
    ) -> GenerationResult:
        response = await self._client.messages.create(
            model=self._model_name,
            max_tokens=1024,
            system=system_prompt_for(ANTHROPIC_SYSTEM_PROMPT, language),
            tools=[CITE_ANSWER_TOOL],
            tool_choice={"type": "tool", "name": "cite_answer"},
            messages=[{"role": "user", "content": _build_user_message(question, chunks)}],
        )

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

    # Ollama defaults to a 4096-token context, which the retrieved passages alone can
    # nearly fill — leaving no room for the answer.
    CONTEXT_TOKENS = 8192
    MAX_OUTPUT_TOKENS = 1024

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

    def _answer_messages(self, question: str, chunks: list[RetrievedChunk], rule_set: str) -> list[dict]:
        return [
            {"role": "system", "content": rule_set},
            {"role": "user", "content": _build_user_message(question, chunks)},
        ]

    async def answer(
        self, question: str, chunks: list[RetrievedChunk], language: Language = "en"
    ) -> GenerationResult:
        context_block = _build_context_block(chunks)

        answer_data, answer_stats = await self._timed_chat(
            self._answer_messages(question, chunks, system_prompt_for(OLLAMA_ANSWER_PROMPT, language)),
            response_schema=None,
        )
        answer_text = answer_data["message"]["content"].strip()
        answer_calls = [answer_stats]
        replies = [answer_data]
        diagnostics: dict = {"think": self._think, "guard_applied": False}

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
        reply = citation_data["message"]["content"]
        schema_error = citation_schema_error(reply)
        try:
            parsed = json.loads(reply)
            cited = [c["chunk_number"] for c in parsed.get("citations", [])]
        except (ValueError, KeyError, TypeError, AttributeError):
            if self._strict_citations:
                raise
            cited = []

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

        calls = [*replies, citation_data]
        return GenerationResult(
            answer=answer_text,
            cited_chunk_numbers=cited,
            input_tokens=sum(c.get("prompt_eval_count", 0) for c in calls),
            output_tokens=sum(c.get("eval_count", 0) for c in calls),
            model_name=self._model_name,
            diagnostics=diagnostics,
        )


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

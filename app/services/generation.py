"""Answer generation with structured, schema-enforced citations.

Two interchangeable providers behind one interface:
- Anthropic: forces the `cite_answer` tool via `tool_choice`.
- Ollama: forces the same JSON schema via Ollama's `format` (constrained decoding).

Both guarantee schema-valid citations without parsing free-form text, so
`/query/ask` never has to care which one is wired in.
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import lru_cache

import httpx
from anthropic import AsyncAnthropic

from app.config import get_settings
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
    async def answer(self, question: str, chunks: list[RetrievedChunk]) -> GenerationResult: ...


class AnthropicGenerationService(GenerationService):
    def __init__(self, api_key: str, model_name: str) -> None:
        self._client = AsyncAnthropic(api_key=api_key)
        self._model_name = model_name

    async def answer(self, question: str, chunks: list[RetrievedChunk]) -> GenerationResult:
        response = await self._client.messages.create(
            model=self._model_name,
            max_tokens=1024,
            system=ANTHROPIC_SYSTEM_PROMPT,
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
    """

    # Ollama defaults to a 4096-token context, which the retrieved passages alone can
    # nearly fill — leaving no room for the answer.
    CONTEXT_TOKENS = 8192
    MAX_OUTPUT_TOKENS = 1024

    def __init__(self, base_url: str, model_name: str, timeout: float = 180.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._model_name = model_name
        self._timeout = timeout

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

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.post(f"{self._base_url}/api/chat", json=payload)
            response.raise_for_status()
            return response.json()

    async def answer(self, question: str, chunks: list[RetrievedChunk]) -> GenerationResult:
        context_block = _build_context_block(chunks)

        answer_data = await self._chat(
            [
                {"role": "system", "content": OLLAMA_ANSWER_PROMPT},
                {"role": "user", "content": _build_user_message(question, chunks)},
            ],
            response_schema=None,
        )
        answer_text = answer_data["message"]["content"].strip()

        citation_data = await self._chat(
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
        parsed = json.loads(citation_data["message"]["content"])

        return GenerationResult(
            answer=answer_text,
            cited_chunk_numbers=[c["chunk_number"] for c in parsed.get("citations", [])],
            input_tokens=answer_data.get("prompt_eval_count", 0)
            + citation_data.get("prompt_eval_count", 0),
            output_tokens=answer_data.get("eval_count", 0) + citation_data.get("eval_count", 0),
            model_name=self._model_name,
        )


@lru_cache
def get_generation_service() -> GenerationService:
    settings = get_settings()
    if settings.generation_provider == "ollama":
        return OllamaGenerationService(settings.ollama_base_url, settings.ollama_model_name)
    return AnthropicGenerationService(settings.anthropic_api_key, settings.claude_model_name)

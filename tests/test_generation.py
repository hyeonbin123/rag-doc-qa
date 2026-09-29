"""The Ollama provider's two-call generation, without a running Ollama.

Under schema-constrained decoding the local 7B model didn't escape quotes inside
string values, so answers containing code were cut off at their first `"`. The answer
is therefore generated as free text, and the citations come from a second call
constrained to a digits-only schema. The recorded answer-quality numbers were measured
with this split, so these tests pin it.
"""

import json
import uuid

import httpx
import pytest

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

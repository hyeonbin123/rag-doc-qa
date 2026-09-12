"""CPU-bound model calls must not stall the event loop.

The embedding models run on the CPU: tens of milliseconds per question, minutes over
a full ingest. Called directly inside an async handler, that time blocks every other
request the server is handling, so model calls go to a bounded pool of worker threads
(see app/services/inference.py).
"""

import asyncio
import threading
import time

import pytest

from app.config import get_settings
from app.dependencies import get_embedder
from app.main import app
from app.services import ingestion
from app.services.inference import run_model
from tests.conftest import FakeEmbeddingService

BLOCK_SECONDS = 0.5


class SlowEmbeddingService(FakeEmbeddingService):
    """Holds its thread for BLOCK_SECONDS per call, the way a real forward pass does."""

    def embed_query(self, text: str) -> list[float]:
        time.sleep(BLOCK_SECONDS)
        return super().embed_query(text)

    def embed_passages(self, texts: list[str]) -> list[list[float]]:
        time.sleep(BLOCK_SECONDS)
        return super().embed_passages(texts)


class OverlapTracker:
    """A stand-in model call that records how many calls were running at once."""

    def __init__(self) -> None:
        self.active = 0
        self.peak = 0
        self._lock = threading.Lock()

    def call(self, _: int) -> None:
        with self._lock:
            self.active += 1
            self.peak = max(self.peak, self.active)
        time.sleep(0.1)
        with self._lock:
            self.active -= 1


async def longest_loop_stall(awaitable):
    """Await `awaitable`; return (longest gap between ticks of a 10 ms heartbeat, result)."""
    gaps: list[float] = []
    done = asyncio.Event()

    async def heartbeat() -> None:
        last = time.perf_counter()
        while not done.is_set():
            await asyncio.sleep(0.01)
            now = time.perf_counter()
            gaps.append(now - last)
            last = now

    beat = asyncio.create_task(heartbeat())
    try:
        result = await awaitable
    finally:
        done.set()
        await beat
    return max(gaps), result


@pytest.mark.asyncio
async def test_question_embedding_does_not_stall_the_event_loop(authed_client):
    app.dependency_overrides[get_embedder] = lambda: lambda language="en": SlowEmbeddingService()

    stall, response = await longest_loop_stall(
        authed_client.post("/query/ask", json={"question": "How do I declare a path parameter?"})
    )

    assert response.status_code == 200
    assert stall < BLOCK_SECONDS / 2


@pytest.mark.asyncio
async def test_ingestion_embedding_does_not_stall_the_event_loop(db_session, monkeypatch):
    async def fake_commit_sha(client, commit_sha=None):
        return "deadbeef"

    async def fake_doc_paths(client, sha, languages):
        return [("docs/en/docs/stall-test.md", "en")]

    async def fake_raw_file(client, sha, path):
        return "# Stall test\n\nPath parameters are declared in the path string.\n"

    monkeypatch.setattr(ingestion, "resolve_commit_sha", fake_commit_sha)
    monkeypatch.setattr(ingestion, "list_doc_paths", fake_doc_paths)
    monkeypatch.setattr(ingestion, "fetch_raw_file", fake_raw_file)

    stall, outcome = await longest_loop_stall(
        ingestion.run_ingestion(db_session, lambda language: SlowEmbeddingService())
    )

    assert outcome.chunks_created > 0
    assert stall < BLOCK_SECONDS / 2


@pytest.mark.asyncio
async def test_model_calls_run_at_most_model_threads_at_a_time():
    # torch already spreads one call over the CPU cores, so the pool is bounded rather
    # than growing with the number of requests in flight.
    limit = get_settings().model_threads
    tracker = OverlapTracker()

    await asyncio.gather(*(run_model(tracker.call, i) for i in range(limit * 2)))

    assert tracker.peak == limit

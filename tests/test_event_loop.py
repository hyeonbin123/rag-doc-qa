"""CPU-bound work must not stall the event loop.

The embedding models run on the CPU: tens of milliseconds per question, minutes over
a full ingest. Called directly inside an async handler, that time blocks every other
request the server is handling, so model calls go to a bounded pool of worker threads
(see app/services/inference.py). bcrypt is the same kind of work: about a quarter
second per login or registration.
"""

# [테스트 묶음] CPU를 오래 쓰는 동기 작업(질문 임베딩, 적재 임베딩, bcrypt)이 이벤트 루프를 멈추지 않는지 재는
# 회귀 테스트. README 설계 판단 '모델 계산은 이벤트 루프 밖에서'의 근거를 코드로 고정한다.
# [왜 중요한가] 비동기 핸들러 안에서 모델을 바로 부르면 그동안 서버 전체가 멈춘다. 질문 6개를 동시에 보내자
# 다른 요청이 최대 0.7초 기다렸고, 관리자 적재 API는 몇 분 동안 서버를 멈출 수
# 있었다(app/services/inference.py docstring, 커밋 5616ba5). 그래서 모델 호출은 크기가 정해진 스레드
# 풀(run_model), bcrypt는 Starlette 스레드 풀(run_in_threadpool)로 옮겼다.
# [방법] '느린 가짜'(time.sleep으로 스레드를 0.5초 잡는 모델)를 넣고, 10ms마다 깨는 하트비트 코루틴의 가장 긴
# 간격을 잰다. 작업이 루프 위에서 돌면 간격이 0.5초 가까이 벌어지고, 스레드로 빠지면 짧게 유지된다.

import asyncio
import threading
import time

# pytest: 비동기 테스트 표시.
import pytest

# 스레드 수 설정(MODEL_THREADS), 바꿔 끼울 임베딩 의존성, 앱, bcrypt 함수를 바꿀 auth 라우터 모듈, 적재
# 서비스, 모델 스레드 풀 함수, 가짜 임베딩 기반 클래스를 가져온다.
from app.config import get_settings
from app.dependencies import get_embedder
from app.main import app
from app.routers import auth as auth_router
from app.services import ingestion
from app.services.inference import run_model
from tests.conftest import FakeEmbeddingService

# 느린 가짜가 호출마다 스레드를 잡는 시간. 판정 기준은 이것의 절반(0.25초)보다 짧은 루프 정지다.
BLOCK_SECONDS = 0.5


# 실제 모델의 순전파처럼 호출마다 스레드를 BLOCK_SECONDS 동안 붙잡는 가짜 임베딩. time.sleep은 GIL을 놓으므로
# 스레드에서 돌면 루프는 계속 돈다.
class SlowEmbeddingService(FakeEmbeddingService):
    """Holds its thread for BLOCK_SECONDS per call, the way a real forward pass does."""

    def embed_query(self, text: str) -> list[float]:
        time.sleep(BLOCK_SECONDS)
        return super().embed_query(text)

    def embed_passages(self, texts: list[str]) -> list[list[float]]:
        time.sleep(BLOCK_SECONDS)
        return super().embed_passages(texts)


# 동시에 몇 개의 호출이 실행 중인지 세는 가짜 모델 호출. 잠금(Lock)으로 카운터를 보호하고 최댓값(peak)을 남겨,
# 스레드 풀 크기 제한을 확인하는 데 쓴다.
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


# 측정 도구: 대상 작업을 기다리는 동안 10ms 간격 하트비트 코루틴을 함께 돌려, 하트비트 사이의 가장 긴
# 간격(루프가 멈춘 최대 시간)과 작업 결과를 돌려준다. 작업이 끝나면 하트비트를 멈추고 기다려 남은 태스크가
# 없게 한다.
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


# /query/ask의 질문 임베딩이 모델 스레드에서 돌아, 0.5초 걸리는 임베딩 동안에도 루프가 0.25초 이상 멈추지
# 않는지 확인한다. 임베딩 의존성은 이 테스트에서만 느린 가짜로 바꾼다.
@pytest.mark.asyncio
async def test_question_embedding_does_not_stall_the_event_loop(authed_client):
    app.dependency_overrides[get_embedder] = lambda: lambda language="en": SlowEmbeddingService()

    stall, response = await longest_loop_stall(
        authed_client.post("/query/ask", json={"question": "How do I declare a path parameter?"})
    )

    assert response.status_code == 200
    assert stall < BLOCK_SECONDS / 2


# 적재(run_ingestion)의 문서 임베딩도 모델 스레드에서 도는지 확인한다. 관리자 적재 API는 API 프로세스 안에서
# 적재를 돌리기 때문이다. GitHub 호출 세 개(커밋, 목록, 원문)는 monkeypatch로 고정 값을 돌려주게 해 네트워크
# 없이 돈다.
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


# 가입의 해시와 로그인의 검증(bcrypt, 호출당 약 0.24초)도 루프를 멈추지 않는지 확인한다. auth 라우터가 함수
# 이름을 직접 import했으므로 라우터 모듈의 속성을 느린 버전으로 바꾼다(커밋 08007dc).
@pytest.mark.asyncio
async def test_password_hashing_does_not_stall_the_event_loop(client, monkeypatch):
    real_hash, real_verify = auth_router.hash_password, auth_router.verify_password

    def slow_hash(password: str) -> str:
        time.sleep(BLOCK_SECONDS)
        return real_hash(password)

    def slow_verify(password: str, hashed_password: str) -> bool:
        time.sleep(BLOCK_SECONDS)
        return real_verify(password, hashed_password)

    monkeypatch.setattr(auth_router, "hash_password", slow_hash)
    monkeypatch.setattr(auth_router, "verify_password", slow_verify)
    credentials = {"email": "stall@example.com", "password": "supersecret1"}

    stall, response = await longest_loop_stall(client.post("/auth/register", json=credentials))
    assert response.status_code == 201
    assert stall < BLOCK_SECONDS / 2

    stall, response = await longest_loop_stall(
        client.post(
            "/auth/login",
            data={"username": credentials["email"], "password": credentials["password"]},
        )
    )
    assert response.status_code == 200
    assert stall < BLOCK_SECONDS / 2


# 모델 스레드 풀이 동시에 MODEL_THREADS개까지만 돌리는지 확인한다. 한도의 두 배를 한꺼번에 넣어도 동시에 도는
# 수의 최댓값이 정확히 한도와 같아야 한다(넘으면 제한이 없는 것, 모자라면 풀을 다 쓰지 못하는 것).
@pytest.mark.asyncio
async def test_model_calls_run_at_most_model_threads_at_a_time():
    # torch already spreads one call over the CPU cores, so the pool is bounded rather
    # than growing with the number of requests in flight.
    limit = get_settings().model_threads
    tracker = OverlapTracker()

    await asyncio.gather(*(run_model(tracker.call, i) for i in range(limit * 2)))

    assert tracker.peak == limit

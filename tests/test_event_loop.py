"""CPU를 쓰는 작업이 이벤트 루프를 멈추게 해서는 안 된다.

임베딩 모델은 CPU에서 돈다: 질문 하나에 수십 ms, 전체 적재에는 몇 분이 걸린다. 비동기 핸들러 안에서
그대로 부르면 그 시간 동안 서버가 처리 중인 다른 요청이 모두 막히므로, 모델 호출은 크기가 정해진 작업
스레드 풀로 보낸다(app/services/inference.py 참고). bcrypt도 같은 종류의 작업이다: 로그인이나 가입 한 번에
약 0.25초.
"""

# [테스트 묶음] CPU를 오래 쓰는 동기 작업(질문 임베딩, 적재 임베딩·청킹·GitHub 클라이언트 생성, bcrypt)이
# 이벤트 루프를 멈추지 않는지 재는 회귀 테스트. README 설계 판단 '모델 계산은 이벤트 루프 밖에서'의 근거를
# 코드로 고정한다.
# [왜 중요한가] 비동기 핸들러 안에서 모델을 바로 부르면 그동안 서버 전체가 멈춘다. 질문 6개를 동시에 보내자
# 다른 요청이 최대 0.7초 기다렸고, 관리자 적재 API는 몇 분 동안 서버를 멈출 수
# 있었다(app/services/inference.py docstring, 커밋 5616ba5). 그래서 모델 호출은 크기가 정해진 스레드
# 풀(run_model), bcrypt는 Starlette 스레드 풀(run_in_threadpool)로 옮겼다.
# [방법] '느린 가짜'(time.sleep으로 스레드를 0.5초 잡는 모델)를 넣고, 10ms마다 깨는 하트비트 코루틴의 가장 긴
# 간격을 잰다. 작업이 루프 위에서 돌면 간격이 0.5초 가까이 벌어지고, 스레드로 빠지면 짧게 유지된다.

import asyncio
import gc
import ssl
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
    """실제 순전파처럼 호출마다 스레드를 BLOCK_SECONDS 동안 붙잡는다."""

    def embed_query(self, text: str) -> list[float]:
        time.sleep(BLOCK_SECONDS)
        return super().embed_query(text)

    def embed_passages(self, texts: list[str]) -> list[list[float]]:
        time.sleep(BLOCK_SECONDS)
        return super().embed_passages(texts)


# 동시에 몇 개의 호출이 실행 중인지 세는 가짜 모델 호출. 잠금(Lock)으로 카운터를 보호하고 최댓값(peak)을 남겨,
# 스레드 풀 크기 제한을 확인하는 데 쓴다.
class OverlapTracker:
    """동시에 몇 개의 호출이 돌고 있었는지 기록하는 가짜 모델 호출."""

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
# 2026-10-29에 두 가지를 더했다.
# - 대상을 시작하기 전에 한 번 양보해(asyncio.sleep(0)) 하트비트가 먼저 시작 시각을 잡게 한다. 그러지 않으면
#   대상 코루틴이 처음 양보할 때까지 하는 동기 작업이 잰 구간 밖에 놓인다. 적재가 GitHub 클라이언트를 만들며
#   CA 번들을 읽는 0.3~0.4초가 그렇게 숨어 있다가, 적재 잠금 질의가 그 앞에 들어오자 비로소 드러났다.
# - 재는 동안에는 순환 GC를 끄고 끝나면 원래 상태로 돌린다. 이 테스트 프로세스는 torch 등을 불러 살아 있는
#   객체가 약 55만 개라 전체 수집 한 번이 약 0.2초(CPU 부하 약 68%에서 3번 재어 0.19~0.20초)이고, 수집은 어느
#   스레드가 일으키든 GIL을 쥔 채 돌아 그동안 루프도 멈춘다. 그 수집이 우연히 재는 구간에 걸리면 코드가 루프
#   위에서 한 일과 상관없이 실패한다. 이 테스트들이 보려는 것은 '동기 작업을 루프 밖으로 보냈는가'이고, 할당
#   자체에 드는 CPU 시간은 그대로 잰다.
async def longest_loop_stall(awaitable):
    """`awaitable`을 기다리고 (10ms 하트비트 사이의 가장 긴 간격, 결과)를 돌려준다."""
    gaps: list[float] = []
    done = asyncio.Event()

    async def heartbeat() -> None:
        last = time.perf_counter()
        while not done.is_set():
            await asyncio.sleep(0.01)
            now = time.perf_counter()
            gaps.append(now - last)
            last = now

    gc_was_enabled = gc.isenabled()
    gc.disable()
    try:
        beat = asyncio.create_task(heartbeat())
        await asyncio.sleep(0)
        try:
            result = await awaitable
        finally:
            done.set()
            await beat
    finally:
        if gc_was_enabled:
            gc.enable()
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


# 적재 테스트용 가짜 GitHub: 커밋·목록·원문 세 호출을 monkeypatch로 고정 값(영어 문서 한 페이지, 본문은
# raw_text)으로 바꿔 네트워크 없이 돈다. 적재의 다른 단계(해시, 청킹, 임베딩, DB 쓰기)는 실제 코드가 돈다.
def serve_single_page(monkeypatch, raw_text: str) -> None:
    async def fake_commit_sha(client, commit_sha=None):
        return "deadbeef"

    async def fake_doc_paths(client, sha, languages):
        return [("docs/en/docs/stall-test.md", "en")]

    async def fake_raw_file(client, sha, path):
        return raw_text

    monkeypatch.setattr(ingestion, "resolve_commit_sha", fake_commit_sha)
    monkeypatch.setattr(ingestion, "list_doc_paths", fake_doc_paths)
    monkeypatch.setattr(ingestion, "fetch_raw_file", fake_raw_file)


# 적재(run_ingestion)의 문서 임베딩도 모델 스레드에서 도는지 확인한다. 관리자 적재 API는 API 프로세스 안에서
# 적재를 돌리기 때문이다.
@pytest.mark.asyncio
async def test_ingestion_embedding_does_not_stall_the_event_loop(db_session, monkeypatch):
    serve_single_page(monkeypatch, "# Stall test\n\nPath parameters are declared in the path string.\n")

    stall, outcome = await longest_loop_stall(
        ingestion.run_ingestion(db_session, lambda language: SlowEmbeddingService())
    )

    assert outcome.chunks_created > 0
    assert stall < BLOCK_SECONDS / 2


# 적재의 청킹(chunk_markdown: 줄마다 tiktoken 인코딩과 정규식)도 이벤트 루프 밖에서 돌아야 한다. 예전에는 루프
# 위에서 동기로 돌아 가장 큰 문서(en/docs/release-notes.md, 약 695,000자)에서 약 0.3~0.4초 멈췄다. 여기서는
# 청커를 BLOCK_SECONDS 동안 자는 느린 가짜로 감싸(결정적) Starlette 스레드 풀로 빠지는지 확인한다.
@pytest.mark.asyncio
async def test_ingestion_chunking_does_not_stall_the_event_loop(db_session, monkeypatch):
    real_chunk_markdown = ingestion.chunk_markdown

    def slow_chunk_markdown(raw_text):
        time.sleep(BLOCK_SECONDS)
        return real_chunk_markdown(raw_text)

    monkeypatch.setattr(ingestion, "chunk_markdown", slow_chunk_markdown)
    serve_single_page(monkeypatch, "# Stall test\n\nPath parameters are declared in the path string.\n")

    stall, outcome = await longest_loop_stall(
        ingestion.run_ingestion(db_session, lambda language: FakeEmbeddingService())
    )

    assert outcome.chunks_created > 0
    assert stall < BLOCK_SECONDS / 2


# 적재가 GitHub 클라이언트를 여는 일도 루프를 멈추지 않아야 한다. httpx는 기본 SSL 컨텍스트를 만들며 certifi
# CA 번들을 동기로 읽는데(ssl.SSLContext.load_verify_locations), Windows 호스트에서 클라이언트 하나에
# 0.3~0.4초가 걸린다(2026-10-29, CPU 부하 약 65%에서 4번 재어 0.32~0.43초). 여기서는 그 읽기를 BLOCK_SECONDS
# 동안 자는 느린 가짜로 감싸 결정적으로 만들고, 클라이언트 생성은 실제 코드(ingestion.github_client)가 돌게
# 둔다(커밋·목록·원문 호출만 가짜). loads는 실제 생성 경로를 지났는지(번들을 읽었는지)를 확인한다.
@pytest.mark.asyncio
async def test_opening_the_github_client_does_not_stall_the_event_loop(db_session, monkeypatch):
    real_load = ssl.SSLContext.load_verify_locations
    loads: list[tuple] = []

    def slow_load(self, *args, **kwargs):
        loads.append(args)
        time.sleep(BLOCK_SECONDS)
        return real_load(self, *args, **kwargs)

    monkeypatch.setattr(ssl.SSLContext, "load_verify_locations", slow_load)
    serve_single_page(monkeypatch, "# Stall test\n\nPath parameters are declared in the path string.\n")

    stall, outcome = await longest_loop_stall(
        ingestion.run_ingestion(db_session, lambda language: FakeEmbeddingService())
    )

    assert loads
    assert outcome.chunks_created > 0
    assert stall < BLOCK_SECONDS / 2


# 릴리스 노트처럼 짧은 글머리 기호 줄이 많은 큰 합성 문서(1,062,850자, 청크 750개). 실제 청커로 약 0.6초(이
# 저장소를 만든 데스크톱에서 CPU 부하 약 68%일 때 3번 재어 0.57~0.73초)가 걸려, 청킹이 루프 위에서 돌면 그
# 시간만큼 멈춘다. 실제 문서 중 가장 큰 en/docs/release-notes.md(약 695,000자)보다 크게 잡아 여유를 둔다.
def large_release_notes() -> str:
    lines = ["# Release Notes\n\n## Latest Changes\n\n"]
    for i in range(7500):
        if i % 400 == 0:
            lines.append(f"\n## 0.{i // 400}.0\n\n### Features\n\n")
        lines.append(
            f"* Update docs for `Query` parameter {i}. "
            f"PR [#{10000 + i}](https://github.com/fastapi/fastapi/pull/{10000 + i}) "
            f"by [@user{i % 97}](https://github.com/user{i % 97}).\n"
        )
    return "".join(lines)


# 실제 청커로도 확인한다: 위 문서를 dry run(임베딩·DB 쓰기 없음)으로 적재하며 루프 정지가 0.2초(README 설계
# 판단 '모델 계산은 이벤트 루프 밖에서'의 다른 요청 최대 대기 기준) 미만인지 본다. 스레드에서 돌면 GIL 전환
# 간격(기본 5ms) 수준의 틈만 생긴다.
@pytest.mark.asyncio
async def test_chunking_a_large_document_does_not_stall_the_event_loop(db_session, monkeypatch):
    serve_single_page(monkeypatch, large_release_notes())

    stall, outcome = await longest_loop_stall(
        ingestion.run_ingestion(db_session, lambda language: FakeEmbeddingService(), dry_run=True)
    )

    assert outcome.chunks_created > 100
    assert stall < 0.2


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
    # torch는 이미 호출 하나를 CPU 코어 여러 개에 나눠 돌리므로, 풀은 처리 중인 요청 수만큼 늘어나지 않고
    # 크기가 제한된다.
    limit = get_settings().model_threads
    tracker = OverlapTracker()

    await asyncio.gather(*(run_model(tracker.call, i) for i in range(limit * 2)))

    assert tracker.peak == limit

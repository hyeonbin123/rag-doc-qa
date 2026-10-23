# [테스트 묶음] 질문 API POST /query/ask(app/routers/query.py)의 통합 테스트. 실제 테스트 DB에 문서·청크를
# 넣고, 임베딩·생성은 가짜로 바꿔 인증, 인용 응답, 질문 기록 저장, DB 연결 반납, 모델별 점수 바닥값, 입력
# 거부를 확인한다.
# [왜 중요한가] 여러 테스트가 실제로 고친 문제의 회귀 방지다: 생성 중에 DB 연결을 잡고 있던 것(커밋
# 53250be), NUL 문자·고립 서로게이트가 든 질문이 LLM 답변까지 마친 뒤 500으로 끝나던 것(ZAP 1차 스캔,
# 커밋 55002dc).

import logging

import pytest

# ASGITransport·AsyncClient: 앱 예외를 테스트로 올리지 않고 500 응답 그대로 받는 클라이언트를 따로 만든다.
from httpx import ASGITransport, AsyncClient

# 바꿔 끼울 의존성(임베딩, 생성기), 앱, 직접 넣을 문서·청크 모델, 바닥값 표(SCORE_FLOORS)를 바꿀 검색 모듈,
# 생성 모듈(생성기 장애 예외), conftest의 가짜와 벡터 차원.
from app.dependencies import get_embedder, get_generator
from app.main import app
from app.models.chunk import Chunk
from app.models.document import Document
from app.services import generation, retrieval
from tests.conftest import EMBEDDING_DIM, FakeEmbeddingService, FakeGenerationService


# 생성기가 불리는 순간에 요청의 DB 세션이 트랜잭션 안에 있는지, 풀에서 빌려 간 연결이 몇 개인지를 기록하는
# 가짜 생성기.
class TransactionProbeGenerator(FakeGenerationService):
    """생성하는 동안 요청의 DB 세션이 아직 연결을 쥐고 있는지 기록한다."""

    def __init__(self, session) -> None:
        self.session = session
        self.in_transaction: bool | None = None
        self.connections_checked_out: int | None = None

    async def answer(self, question, chunks, language="en"):
        self.in_transaction = self.session.in_transaction()
        self.connections_checked_out = self.session.bind.pool.checkedout()
        return await super().answer(question, chunks, language)


# 토큰 없이 질문하면 401.
@pytest.mark.asyncio
async def test_ask_requires_auth(client):
    resp = await client.post("/query/ask", json={"question": "How do path params work?"})
    assert resp.status_code == 401


# 질문과 같은 가짜 벡터를 가진 청크 하나를 넣으면(코사인 1.0), 답과 함께 그 청크의 문서 경로가 인용으로 나오고
# 단계별 지연(latency_ms)이 들어 있는지 확인한다. 청크의 language를 주지 않으면 DB 기본값 'en'이 들어가 영어
# 질문 검색에 걸린다.
@pytest.mark.asyncio
async def test_ask_returns_answer_with_citations(authed_client, db_session):
    fake_embedder = FakeEmbeddingService()
    vector = fake_embedder.embed_query("How do path params work?")

    document = Document(
        source_path="docs/en/docs/tutorial/path-params.md",
        title="Path Parameters",
        source_commit_sha="deadbeef",
        content_hash="hash-path-params",
    )
    db_session.add(document)
    await db_session.flush()

    chunk = Chunk(
        document_id=document.id,
        chunk_index=0,
        heading_path="Tutorial > Path Parameters",
        content="You can declare path parameters using type hints.",
        token_count=10,
        embedding=vector,
    )
    db_session.add(chunk)
    await db_session.commit()

    resp = await authed_client.post(
        "/query/ask", json={"question": "How do path params work?", "top_k": 3}
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["answer"].startswith("Fake answer for:")
    assert len(body["citations"]) >= 1
    assert body["citations"][0]["source_path"] == "docs/en/docs/tutorial/path-params.md"
    assert body["latency_ms"]["total"] >= 0


# 질문마다 질문 기록(query_logs)이 저장되고, 응답의 query_log_id로 /logs에서 다시 볼 수 있는지 확인한다.
# 검색할 청크가 없어도 기록은 남는다.
@pytest.mark.asyncio
async def test_ask_persists_query_log(authed_client, db_session):
    resp = await authed_client.post("/query/ask", json={"question": "What is FastAPI?"})
    assert resp.status_code == 200
    log_id = resp.json()["query_log_id"]

    log_resp = await authed_client.get(f"/logs/{log_id}")
    assert log_resp.status_code == 200
    assert log_resp.json()["question"] == "What is FastAPI?"


# LLM 생성 중에는 요청이 DB 트랜잭션을 끝내고 풀 연결을 반납했어야 한다(빌려 간 연결 0). 생성은 몇 초 걸리고
# Ollama는 한 번에 한 요청씩 답하므로, 연결을 쥔 채 기다리면 다른 엔드포인트가 연결을 못 얻는다. 질문 기록은
# 그 뒤 짧은 트랜잭션으로 따로 저장된다.
@pytest.mark.asyncio
async def test_ask_releases_db_connection_during_generation(authed_client, db_session):
    probe = TransactionProbeGenerator(db_session)
    app.dependency_overrides[get_generator] = lambda: probe

    resp = await authed_client.post("/query/ask", json={"question": "What is FastAPI?"})

    assert resp.status_code == 200
    assert probe.in_transaction is False
    assert probe.connections_checked_out == 0
    # 질문 기록은 그 뒤에 따로 짧은 트랜잭션으로 저장된다.
    log_resp = await authed_client.get(f"/logs/{resp.json()['query_log_id']}")
    assert log_resp.status_code == 200


# 모든 질문을 첫 번째 축 단위 벡터로 만드는 가짜 임베딩. 그러면 청크의 코사인 점수가 그 청크 벡터의 첫 성분과
# 같아져, 점수를 원하는 값으로 정확히 맞출 수 있다.
class AxisEmbeddingService(FakeEmbeddingService):
    """모든 질문을 첫 번째 축으로 임베딩한다. 그래서 청크의 점수가 그 벡터의 첫 성분과 같다."""

    def __init__(self) -> None:
        self.model_name = "axis-embedding"

    def embed_query(self, text: str) -> list[float]:
        return [1.0] + [0.0] * (EMBEDDING_DIM - 1)


# 질문을 임베딩한 모델의 바닥값이 검색에 쓰이는지 확인한다. 점수 0.25인 청크는 공통 바닥값 0.3에서는 잘려
# 인용이 비고, 그 모델의 바닥값을 0.2로 넣으면(SCORE_FLOORS, monkeypatch로 테스트 뒤 되돌림)
# 인용된다(docs/experiments.md v12 모델별 바닥값).
@pytest.mark.asyncio
async def test_ask_uses_the_score_floor_of_the_embedding_model(authed_client, db_session, monkeypatch):
    document = Document(
        source_path="docs/en/docs/tutorial/body.md",
        title="Body",
        source_commit_sha="deadbeef",
        content_hash="hash-body",
    )
    db_session.add(document)
    await db_session.flush()
    db_session.add(
        Chunk(
            document_id=document.id,
            chunk_index=0,
            heading_path="Body",
            content="Declare a Pydantic model.",
            token_count=5,
            # 단위 벡터를 유지하도록 두 번째 성분을 sqrt(1 − 0.25²)로 둔다. 첫 성분 0.25가 곧 질문 벡터와의
            # 코사인이다.
            embedding=[0.25, (1 - 0.25**2) ** 0.5] + [0.0] * (EMBEDDING_DIM - 2),  # 코사인 0.25
        )
    )
    await db_session.commit()
    app.dependency_overrides[get_embedder] = lambda: lambda language="en": AxisEmbeddingService()

    under_shared_floor = await authed_client.post("/query/ask", json={"question": "Body?"})
    monkeypatch.setitem(retrieval.SCORE_FLOORS, "axis-embedding", 0.2)
    under_model_floor = await authed_client.post("/query/ask", json={"question": "Body?"})

    assert under_shared_floor.json()["citations"] == []
    assert [c["source_path"] for c in under_model_floor.json()["citations"]] == [
        "docs/en/docs/tutorial/body.md"
    ]


# 생성기가 몇 번 불렸는지 세는 가짜. 거부된 요청이 LLM까지 가지 않았는지 확인한다.
class CountingGenerator(FakeGenerationService):
    def __init__(self) -> None:
        self.calls = 0

    async def answer(self, question, chunks, language="en"):
        self.calls += 1
        return await super().answer(question, chunks, language)


# 질문에 NUL 문자가 있으면(영어·한국어 모두) 요청 검증에서 422로 끝나야 하고, 생성기는 한 번도 불리지 않으며
# 기록도 남지 않아야 한다. PostgreSQL 문자열에 U+0000을 저장할 수 없어, 예전에는 LLM 답변까지 마친 뒤 마지막
# commit에서 500이 났다.
@pytest.mark.asyncio
@pytest.mark.parametrize("question", ["What is\x00FastAPI?", "경로 매개변수는\x00 어떻게 선언하나요?"])
async def test_ask_rejects_a_nul_character_before_answering(authed_client, question):
    generator = CountingGenerator()
    app.dependency_overrides[get_generator] = lambda: generator

    resp = await authed_client.post("/query/ask", json={"question": question})

    assert resp.status_code == 422
    assert resp.json()["detail"][0]["loc"] == ["body", "question"]
    assert generator.calls == 0
    assert (await authed_client.get("/logs")).json() == []


# 고립 서로게이트(\ud800)가 든 질문도 500이 아니라 422여야 한다. UTF-8로 나타낼 수 없는 문자라, 422 응답
# 본문이 입력을 그대로 되돌려 주다가 인코딩에서 500이 났었다. JSON을 직접 바이트로 보내야 이런 입력을 만들 수
# 있다.
@pytest.mark.asyncio
async def test_ask_rejects_a_lone_surrogate(authed_client):
    # JSON은 UTF-16 쌍의 반쪽도 적을 수 있는데, 이것은 UTF-8로 나타낼 수 없어 임베딩도 저장도 할 수 없다.
    # Pydantic은 이를 문자열로 받지 않지만, 422 본문이 입력을 되돌려 주므로 그것을 UTF-8로 인코딩하던 예전
    # 처리에서는 거부 응답이 500이 되었다.
    resp = await authed_client.post(
        "/query/ask",
        content=rb'{"question": "What is \ud800 FastAPI?"}',
        headers={"Content-Type": "application/json"},
    )

    assert resp.status_code == 422
    assert resp.json()["detail"][0]["loc"] == ["body", "question"]


# 채팅 화면(app/web/static/chat.js)은 질문 422의 거부 이유(type)로 안내 문구를 고른다: string_too_long이면
# 길이 안내, 그 밖에는 '보낼 수 없는 문자' 안내. 예전 화면은 NUL 문자 422에도 '2000자 이내' 안내를 보였다.
# 화면이 기대는 서버 응답의 type을 고정한다.
@pytest.mark.asyncio
async def test_a_too_long_question_and_a_nul_character_differ_in_the_422_type(authed_client):
    too_long = await authed_client.post("/query/ask", json={"question": "x" * 2001})
    with_nul = await authed_client.post("/query/ask", json={"question": "What is\x00FastAPI?"})

    assert too_long.status_code == with_nul.status_code == 422
    assert [d["type"] for d in too_long.json()["detail"]] == ["string_too_long"]
    assert "string_too_long" not in [d["type"] for d in with_nul.json()["detail"]]


# 생성기가 답 대신 예외를 내는 가짜. 생성기 장애(GenerationUnavailableError)와 예기치 않은
# 버그(RuntimeError)를 흉내 낸다.
class FailingGenerator(FakeGenerationService):
    def __init__(self, error: Exception) -> None:
        self.error = error

    async def answer(self, question, chunks, language="en"):
        raise self.error


# 생성기 장애(Ollama 꺼짐, 시간 초과, 모델 태그 없음)는 500이 아니라 503과 detail.code, Retry-After로 알린다.
# 채팅 화면은 code로 안내 문구를 고른다(app/web/static/chat.js). 업스트림 오류 본문은 응답에 싣지 않고 서버
# 로그에만 남기며, 응답에도 보안 헤더 세 개가 붙는다. 생성은 질문 기록 저장 전 단계라 query_logs에 행이 생기지
# 않는다.
@pytest.mark.asyncio
@pytest.mark.parametrize("code", ["generator_unavailable", "generator_timeout", "generator_model_missing"])
async def test_a_generator_outage_is_a_503_with_a_code_and_no_query_log(authed_client, caplog, code):
    error = generation.GenerationUnavailableError(code, upstream="Ollama HTTP 404: upstream-only detail")
    app.dependency_overrides[get_generator] = lambda: FailingGenerator(error)

    with caplog.at_level(logging.WARNING):
        resp = await authed_client.post("/query/ask", json={"question": "What is FastAPI?"})

    assert resp.status_code == 503
    assert resp.json()["detail"] == {"code": code, "message": error.message}
    assert resp.headers["retry-after"] == str(error.retry_after)
    assert "upstream-only detail" not in resp.text
    assert "upstream-only detail" in caplog.text
    assert resp.headers["x-content-type-options"] == "nosniff"
    assert resp.headers["x-frame-options"] == "DENY"
    assert "frame-ancestors 'none'" in resp.headers["content-security-policy"]
    assert (await authed_client.get("/logs")).json() == []


# 예기치 않은 예외의 500은 Starlette가 사용자 미들웨어 바깥(ServerErrorMiddleware)에서 만들어 보안 헤더
# 미들웨어를 지나지 않는다. 앱의 500 처리기가 같은 헤더를 직접 붙이는지, 본문은 예외 내용 없이 예전과 같은
# 'Internal Server Error'인지 확인한다. 기본 테스트 클라이언트는 앱 예외를 테스트로 올리므로, 응답을 받으려고
# raise_app_exceptions=False 클라이언트를 따로 만든다(인증 헤더는 authed_client의 것을 쓴다).
@pytest.mark.asyncio
async def test_an_unexpected_error_is_a_plain_500_that_keeps_the_security_headers(authed_client):
    app.dependency_overrides[get_generator] = lambda: FailingGenerator(RuntimeError("bug in the generator"))
    transport = ASGITransport(app=app, raise_app_exceptions=False)

    async with AsyncClient(
        transport=transport, base_url="http://test", headers=authed_client.headers
    ) as raw_client:
        resp = await raw_client.post("/query/ask", json={"question": "What is FastAPI?"})

    assert resp.status_code == 500
    assert resp.text == "Internal Server Error"
    assert resp.headers["x-content-type-options"] == "nosniff"
    assert resp.headers["x-frame-options"] == "DENY"
    assert "frame-ancestors 'none'" in resp.headers["content-security-policy"]
    assert (await authed_client.get("/logs")).json() == []

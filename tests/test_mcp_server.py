# [테스트 묶음] 읽기 전용 MCP 검색 도구(app/mcp_server.py)의 시험. 실제 pgvector 테스트 DB에 문서·청크를
# 넣고 임베딩은 가짜로 바꿔, 모델 파일이나 외부 API 없이 도구의 동작을 SQL까지 포함해 확인한다.
# [무엇을 보나]
# - 도구가 하나뿐이고 읽기 전용 힌트를 단 채 나가는지, 모델에게 가는 글(도구 설명·인자 설명·서버 안내문)이
#   정한 영어 문안 그대로인지.
# - 같은 질문에 HTTP 경로 /query/ask와 같은 청크를 같은 순서·점수로 돌려주는지(검색 경로를 같은 함수로 같은
#   순서로 밟는다는 약속). 질문 기록은 남기지 않는지.
# - 읽기 전용을 서버 코드가 직접 지키는지: 검색 세션이 쓰기를 거절하고, 세션을 나가면 정확 탐색 고정(SET
#   LOCAL)이 풀린다. MCP의 readOnlyHint는 힌트일 뿐 SDK가 쓰기를 막아 주지 않는다.
# - 잘못된 입력은 DB 일을 하기 전에 거절하고, DB나 모델이 안 될 때는 짧은 영어 오류만 돌려준다(DB
#   주소·비밀번호·예외 글을 오류에도 로그에도 싣지 않는다).
# - 자식 프로세스: stdio 전송으로 실제 서버를 띄워 표준 출력에 프로토콜 말고는 아무것도 섞이지 않는지,
#   모듈을 불러오는 것만으로는 서버를 만들지 않는지, HTTP 서비스(app.main)가 이 모듈과 mcp 패키지를 불러오지
#   않는지.
# [방법과 주의]
# - 같은 프로세스 안의 호출은 Client(build_server())로 한다. Client를 async 픽스처로 열면 이 저장소의
#   pytest-asyncio auto 모드에서 teardown이 'Attempted to exit cancel scope in a different task than it was
#   entered in'으로 깨진다. 그래서 시험 본문 안에서 async with로 여는 도우미(_connected_client)를 쓴다.
# - 모듈 수준 전역(async_session_maker, get_embedding_service, get_settings)은 monkeypatch로 바꿔 끼운다.
#   도구는 인자가 None일 때 부를 때마다 그 전역을 읽으므로 바뀐 값이 쓰인다.
# - 자식 프로세스를 띄우는 시험은 셋이다. HTTP 앱(app.main)을 불러오는 것은 모델 라이브러리(torch 등) 때문에
#   20초 안팎이 걸릴 수 있어 제한 시간을 120초로 둔다. 도구 모듈(app.mcp_server)은 그 라이브러리를 첫 호출
#   때 불러오므로 몇 초 안에 뜬다(그것도 시험한다). 이 셋에는 모델이나 DB 접속이 필요한 호출을 넣지
#   않는다(CI에는 모델 캐시가 없다).

import logging
import os
import re
import subprocess
import sys
import threading
import time
import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

import anyio
import pytest

# Client·StdioServerParameters: 같은 프로세스 안의 서버(Client(서버 객체))와 자식 프로세스(stdio)에 붙는
# 공식 클라이언트. get_default_environment: SDK의 stdio 클라이언트가 자식에게 물려주는 '안전한 환경 변수
# 목록'이다.
from mcp import Client, StdioServerParameters
from mcp.client.stdio import get_default_environment
from pydantic import ValidationError

# text: 시험 DB에 직접 보내는 SQL(행 수, SHOW, 쓰기 시도). DBAPIError: 읽기 전용 트랜잭션이 쓰기를 거절할 때
# SQLAlchemy가 올리는 예외. async_sessionmaker·create_async_engine: 시험 DB의 세션 팩토리와, 일부러 닿지
# 않는 DB·연결 하나짜리 풀에 붙는 엔진.
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

# mcp_server: 모듈 수준 전역을 바꿔 끼우려고 모듈째 가져온다. db_session_module: 서버가 나갈 때 닫는 엔진이
# 이 모듈의 engine이라, 닫는 호출을 세려고 바꿔 끼운다. app: HTTP 경로와 같은 질문을 비교하는 시험이 설정을
# 바꿔 끼운다. retrieve: 읽기 전용 세션 안에서 검색을 직접 부르는 시험용. retrieval: 모델별 점수
# 바닥값(SCORE_FLOORS)을 시험 동안만 바꿔 끼우려고 모듈째 가져온다.
from app import mcp_server
from app.config import get_settings
from app.db import session as db_session_module
from app.main import app
from app.mcp_server import EmbeddingUnavailable, build_server, read_only_session, search_docs
from app.models.chunk import Chunk
from app.models.document import Document
from app.models.query_log import QueryLog
from app.services import retrieval
from app.services.reranking import RerankerService
from app.services.retrieval import retrieve
from tests.conftest import EMBEDDING_DIM, FakeEmbeddingService

REPO_ROOT = Path(__file__).resolve().parent.parent
TOOL = "search_fastapi_docs"
# 자식 프로세스 시험의 제한 시간(초). HTTP 앱을 불러오는 것만으로 20초 안팎이 걸릴 수 있다.
CHILD_TIMEOUT_SECONDS = 120

# 모델에게 가는 글의 정한 영어 문안(도구 설명, 인자 설명, 서버 안내문). 한 글자라도 바뀌면 시험이 알려 준다.
EXPECTED_TOOL_DESCRIPTION = (
    "Search the FastAPI documentation (English originals and Korean translations) and return the most "
    "relevant passages with their source paths. Read-only: it runs the same retrieval as this project's "
    "HTTP API (question language detection, same-language embedding, RETRIEVAL_MODE search) and neither "
    "generates an answer nor stores the question. Ask in English to search the English docs or in Korean "
    "to search the Korean translations; set language to override the detection. Results are ranked, not "
    "verified: a question the docs do not cover can still return weakly related passages, and the hits "
    "list can also be empty. Check the content before relying on a hit."
)
EXPECTED_ARGUMENT_DESCRIPTIONS = {
    "question": "The question to search for (1-2000 characters).",
    "top_k": "How many passages to return (1-10).",
    "language": (
        "Which translation to search: auto picks Korean when the question contains Hangul, otherwise English."
    ),
}
EXPECTED_INSTRUCTIONS = (
    "Read-only search over the FastAPI documentation corpus of this project. Call search_fastapi_docs to "
    "find passages, and cite source_path when you use them."
)
# 도구가 돌려주는 오류 문안(모델이 읽는 글이라 정한 문안 그대로여야 한다).
DATABASE_ERROR = (
    "The document database could not be queried. Check that it is running and migrated, then try again."
)
EMBEDDING_ERROR = (
    "The embedding or reranking model could not be loaded or run. "
    "Check the model cache (HF_HOME) and the network."
)

# 영어·한국어 질문. 한글이 하나라도 있으면 한국어 문서에서 찾는다(app/services/language.py).
QUESTIONS = {"en": "How do path params work?", "ko": "경로 매개변수는 어떻게 선언하나요?"}


# 자식 프로세스(stdio 서버와 subprocess.run으로 띄우는 파이썬)에 줄 환경 변수. 두 가지를 합친다.
# - SDK의 안전 목록(PATH, Windows의 SYSTEMROOT 등): subprocess.run에 환경을 직접 주면 부모 환경이 하나도 안
#   넘어가는데, Windows에서는 SYSTEMROOT가 없으면 파이썬이 asyncio조차 불러오지 못한다(WinError 10106).
#   stdio 클라이언트는 이 목록을 알아서 깔지만, 세 시험이 같은 환경을 쓰도록 여기서 한 번에 만든다.
# - 앱 설정 DATABASE_URL·JWT_SECRET_KEY: 부모의 os.environ에 있는 것만 옮긴다. SDK의 stdio 클라이언트는 부모
#   환경을 물려주지 않는다. CI는 두 값을 환경 변수로 주지만, README대로 .env만 두고 pytest를 돌리는 로컬에는
#   os.environ에 없다. 그때는 cwd를 저장소 루트로 줘 자식의 설정이 .env에서 읽게 한다. 없는 키를 None이나 빈
#   값으로 넣으면 .env의 값을 덮어쓰므로 넣지 않는다.
def _child_env() -> dict[str, str]:
    env = get_default_environment()
    for key in ("DATABASE_URL", "JWT_SECRET_KEY"):
        if key in os.environ:
            env[key] = os.environ[key]
    return env


# 같은 프로세스 안에서 새 서버에 붙는 MCP 클라이언트. 시험 본문 안에서만 쓴다(async 픽스처로 열면 teardown이
# 깨진다. 위 머리 주석). raise_exceptions=True여도 도구의 실패는 예외가 아니라 is_error=True인 결과로 온다.
@asynccontextmanager
async def _connected_client() -> AsyncIterator[Client]:
    async with Client(build_server(), raise_exceptions=True) as client:
        yield client


# 도구 결과(CallToolResult)의 첫 글 조각. 오류면 모델이 읽는 오류 글이고, 성공이면 결과의 JSON 글이다.
def _text(result) -> str:
    return result.content[0].text


# 시험 DB에 붙는 세션 팩토리. 서버의 전역 async_session_maker 자리에 끼우거나 search_docs에 직접 넘긴다.
@pytest.fixture
def session_factory(db_engine):
    return async_sessionmaker(db_engine, expire_on_commit=False)


# 모듈의 설정을 dense 검색으로 고정한다. .env에 RETRIEVAL_MODE가 다른 값으로 적힌 PC에서도 시험이 같은
# 모드로 돌게 하려는 것이다(rerank 모드 시험은 설정을 직접 만든다).
@pytest.fixture
def dense_settings(monkeypatch):
    settings = get_settings().model_copy(update={"retrieval_mode": "dense"})
    monkeypatch.setattr(mcp_server, "get_settings", lambda: settings)
    return settings


# 도구가 시험 DB와 가짜 임베딩으로 검색하게 모듈 전역을 바꿔 끼운다.
@pytest.fixture
def patched_search(monkeypatch, session_factory, dense_settings):
    monkeypatch.setattr(mcp_server, "async_session_maker", session_factory)
    monkeypatch.setattr(mcp_server, "get_embedding_service", lambda _language: FakeEmbeddingService())


# 문서 하나와 그 청크 하나를 지정한 언어·본문·벡터로 넣고 커밋한다(tests/test_query.py의 방식). 문서 경로는
# 실제와 같은 docs/<언어>/docs/<이름>.md 꼴이다.
async def _add_chunk(
    db_session, language: str, name: str, content: str, vector: list[float], heading: str = "Tutorial"
):
    document = Document(
        source_path=f"docs/{language}/docs/{name}.md",
        title=name,
        source_commit_sha="deadbeef",
        content_hash=f"hash-{language}-{name}",
    )
    db_session.add(document)
    await db_session.flush()
    chunk = Chunk(
        document_id=document.id,
        chunk_index=0,
        heading_path=heading,
        content=content,
        token_count=10,
        embedding=vector,
        language=language,
    )
    db_session.add(chunk)
    await db_session.commit()
    return document, chunk


# 영어·한국어 각각에 청크 둘을 넣는다: 질문과 같은 벡터(코사인 1.0)의 청크와, 다른 글의 벡터(코사인 0.75
# 안팎, 바닥값 0.3 위)의 청크. 어느 질문이든 같은 언어의 두 청크가 바닥값을 넘으므로 순서가 정해져 있고,
# 다른 언어의 청크가 섞이면 결과 수가 달라져 드러난다.
async def _seed_both_languages(db_session) -> None:
    fake = FakeEmbeddingService()
    for language, question in QUESTIONS.items():
        best = f"best passage ({language})"
        other = f"other passage ({language})"
        await _add_chunk(db_session, language, f"{language}-best", best, fake.embed_query(question))
        await _add_chunk(
            db_session, language, f"{language}-other", other, fake.embed_query("an unrelated sentence")
        )


# 불리면 횟수를 세고 곧바로 실패하는 세션 팩토리. 'DB 일을 하기 전에 거절했다'를 팩토리가 불리지
# 않았다(calls == 0)로 확인하는 데 쓴다. AssertionError는 도구가 DB 오류로 옮기지 않는 예외라, 잘못 불리면
# 호출 횟수로도 드러난다.
class SessionFactorySpy:
    def __init__(self) -> None:
        self.calls = 0

    def __call__(self):
        self.calls += 1
        raise AssertionError("the session factory must not be called")


# cross-encoder 대신 쓰는 가짜 재정렬기(tests/test_retrieval.py의 것과 같은 생각): 패시지에 키워드가 있으면
# 1.0, 없으면 0.0. 실제 모델은 올리지 않는다.
class KeywordReranker(RerankerService):
    def __init__(self, keyword: str) -> None:  # 실제 모델 로딩을 일부러 건너뛴다
        self.keyword = keyword

    def score(self, question: str, passages: list[str]) -> list[float]:
        return [1.0 if self.keyword in passage else 0.0 for passage in passages]


# 질문을 늘 첫 축의 단위 벡터로 임베딩하는 가짜(tests/test_query.py의 것과 같은 생각). 청크 벡터의 첫 성분이
# 곧 질문과의 코사인이 되어, 점수 바닥값 바로 아래·위의 청크를 정확히 만들 수 있다. 모델 이름을 따로 둬
# 모델별 바닥값(SCORE_FLOORS)을 이 가짜에만 걸 수 있다.
class AxisEmbeddingService(FakeEmbeddingService):
    def __init__(self) -> None:
        self.model_name = "axis-embedding"

    def embed_query(self, text: str) -> list[float]:
        return [1.0] + [0.0] * (EMBEDDING_DIM - 1)


# 서버가 나갈 때 닫는 엔진 대역. dispose가 몇 번 불렸는지만 센다.
class EngineRecorder:
    def __init__(self) -> None:
        self.disposed = 0

    async def dispose(self) -> None:
        self.disposed += 1


# 도구는 하나뿐이고(검색), 읽기 전용·비파괴·멱등·닫힌 세계 힌트를 달고 나간다. 입력은
# question·top_k·language이고 필수는 question뿐이다. 힌트는 MCP 클라이언트가 확인 절차를 고르는 데 쓰는
# 정보라, 도구가 늘거나 힌트가 빠지면 여기서 알아챈다.
@pytest.mark.asyncio
async def test_server_exposes_one_read_only_tool():
    async with _connected_client() as client:
        listing = await client.list_tools()

    assert [tool.name for tool in listing.tools] == [TOOL]
    tool = listing.tools[0]
    assert tool.title == "FastAPI 문서 검색"
    assert tool.annotations.read_only_hint is True
    assert tool.annotations.destructive_hint is False
    assert tool.annotations.idempotent_hint is True
    assert tool.annotations.open_world_hint is False
    assert set(tool.input_schema["properties"]) == {"question", "top_k", "language"}
    assert tool.input_schema["required"] == ["question"]
    assert tool.description.strip()


# 모델에게 가는 글(도구 설명, 인자 설명, 서버 안내문)이 정한 영어 문안 그대로인지 본다. 줄바꿈과 공백의
# 차이는 무시한다. 이 글은 읽는 모델이 도구를 쓸지·결과를 어떻게 읽을지 정하는 근거라(특히 '결과는 순위일
# 뿐 확인이 아니고, 문서가 다루지 않는 질문에도 약한 조각이 올 수 있다'는 끝 문장들), 코드를 고치다 문안이
# 바뀌면 의도한 변경인지 확인하게 한다.
@pytest.mark.asyncio
async def test_model_facing_texts_keep_the_agreed_english_wording():
    async with _connected_client() as client:
        listing = await client.list_tools()
        instructions = client.instructions

    tool = listing.tools[0]
    assert " ".join(tool.description.split()) == EXPECTED_TOOL_DESCRIPTION
    properties = tool.input_schema["properties"]
    descriptions = {name: spec["description"] for name, spec in properties.items()}
    assert descriptions == EXPECTED_ARGUMENT_DESCRIPTIONS
    assert instructions == EXPECTED_INSTRUCTIONS


# 서버 객체를 만드는 것(MCPServer 생성)이 루트 로거를 건드리지 않는지 본다. SDK는 생성할 때 루트 로거에
# 핸들러가 하나도 없으면 자기 핸들러(rich)를 달고 수준을 INFO로 바꾼다. 실제 실행에서는 main()이 앱의
# configure_logging()을 먼저 불러 핸들러가 있으므로 SDK가 아무것도 바꾸지 않지만, 시험이나 다른 프로그램이
# build_server()를 부르면 그 프로세스의 로깅이 바뀐다. pytest는 늘 캡처 핸들러를 달아 두므로, 핸들러를
# 비워야 이 시험이 실패할 수 있다. 수준은 같은 값을 직접 대입해 두어 monkeypatch가 시험 뒤에 되돌리게 한다.
def test_building_the_server_leaves_root_logging_alone(monkeypatch):
    root = logging.getLogger()
    level_before = root.level
    monkeypatch.setattr(root, "handlers", [])
    monkeypatch.setattr(root, "level", level_before)

    build_server()

    assert root.handlers == []
    assert root.level == level_before


# 임베딩 모델을 올리거나 돌리다 난 실패(예: 모델 캐시가 없고 네트워크도 없을 때의 OSError)가 'DB에 닿지
# 못함'으로 보이면 안 된다. 오류 글은 모델 쪽을 가리키고, DB 세션은 열지도 않는다. 로그에는 예외의 종류
# 이름만 남고 예외 글은 남지 않는다.
@pytest.mark.asyncio
async def test_model_failure_is_not_reported_as_a_database_failure(monkeypatch, dense_settings, caplog):
    spy = SessionFactorySpy()

    def embedder_without_cache(_language):
        raise OSError("model files missing and no network: secret-cache-location")

    monkeypatch.setattr(mcp_server, "async_session_maker", spy)
    monkeypatch.setattr(mcp_server, "get_embedding_service", embedder_without_cache)

    with caplog.at_level(logging.INFO):
        async with _connected_client() as client:
            result = await client.call_tool(TOOL, {"question": QUESTIONS["en"]})

    assert result.is_error is True
    assert "model" in _text(result)
    assert "database" not in _text(result).lower()
    assert EMBEDDING_ERROR in _text(result)
    assert spy.calls == 0
    assert "stage=embedding error=OSError" in caplog.text
    assert "secret-cache-location" not in caplog.text


# rerank 모드에서 재정렬 모델을 올리다 난 실패도 모델 쪽의 실패라 DB 오류로 덮지 않는다. 재정렬 모델은 DB
# 세션을 열기 전에 올리므로 세션 팩토리는 불리지 않는다.
@pytest.mark.asyncio
async def test_reranker_load_failure_is_not_reported_as_a_database_failure():
    spy = SessionFactorySpy()
    rerank_settings = get_settings().model_copy(update={"retrieval_mode": "rerank"})

    def reranker_without_cache(_language):
        raise OSError("reranker files missing and no network")

    with pytest.raises(EmbeddingUnavailable) as raised:
        await search_docs(
            QUESTIONS["en"],
            session_factory=spy,
            embedder_for=lambda _language: FakeEmbeddingService(),
            reranker_for=reranker_without_cache,
            settings=rerank_settings,
        )

    assert isinstance(raised.value.__cause__, OSError)
    assert spy.calls == 0


# 모듈을 불러오는 것만으로는 서버 객체를 만들지 않는다. MCPServer 생성은 로깅을 설정하므로(위 시험),
# 불러오는 것만으로 프로세스의 로깅이 바뀌고 모듈 안에 서버 객체가 남는다. 표준 출력에는 한 바이트도 쓰지
# 않는다: stdio 서버는 서비스를 시작한 뒤에야 표준 출력을 프로토콜 전용으로 돌려놓으므로, 그 전(모듈을
# 불러올 때)의 출력은 프로토콜에 섞인다.
# 모델 라이브러리(torch, sentence-transformers, transformers)도 불러오지 않는다. 불러오는 데만 10초 안팎이
# 걸려, 모듈을 불러올 때 끌어오면 서버가 뜨는 시간이 그만큼 늘고 클라이언트의 초기화 대기 시간을 넘길 수
# 있다. 그 라이브러리는 첫 검색 호출이 임베딩 서비스를 찾을 때 불러온다.
def test_importing_the_module_builds_no_server():
    code = (
        "import logging\n"
        "import sys\n"
        "import app.mcp_server as module\n"
        "from mcp.server.mcpserver import MCPServer\n"
        "assert logging.root.handlers == [], logging.root.handlers\n"
        "assert not any(isinstance(value, MCPServer) for value in vars(module).values())\n"
        "libraries = ('torch', 'sentence_transformers', 'transformers')\n"
        "heavy = [name for name in libraries if name in sys.modules]\n"
        "assert not heavy, heavy\n"
    )

    done = subprocess.run(
        [sys.executable, "-c", code],
        cwd=REPO_ROOT,
        env=_child_env(),
        capture_output=True,
        timeout=CHILD_TIMEOUT_SECONDS,
    )

    assert done.returncode == 0, done.stderr.decode(errors="replace")
    assert done.stdout == b""


# 도구 모듈의 get_embedding_service·get_reranker_service는 서비스 모듈(app/services/embedding.py,
# reranking.py)의 같은 이름 함수를 불릴 때 불러와 그대로 부르는 포장이다(모델 라이브러리를 첫 호출 때
# 불러오려는 것). 포장이 다른 서비스를 만들거나 인자를 바꾸면 HTTP 경로와 다른 모델로 검색하게 되므로,
# 서비스 모듈의 함수를 대역으로 바꿔 '받은 언어를 그대로 넘기고 돌려받은 것을 그대로 돌려준다'를 확인한다.
def test_default_lookups_delegate_to_the_service_modules(monkeypatch):
    from app.services import embedding, reranking

    asked: list[tuple[str, str]] = []
    embedder, reranker = object(), object()

    def fake_embedding_service(language):
        asked.append(("embedding", language))
        return embedder

    def fake_reranker_service(language):
        asked.append(("reranking", language))
        return reranker

    monkeypatch.setattr(embedding, "get_embedding_service", fake_embedding_service)
    monkeypatch.setattr(reranking, "get_reranker_service", fake_reranker_service)

    assert mcp_server.get_embedding_service("ko") is embedder
    assert mcp_server.get_reranker_service("en") is reranker
    assert asked == [("embedding", "ko"), ("reranking", "en")]


# 같은 질문·같은 top_k에서 MCP 도구가 /query/ask와 같은 청크를 같은 순서·같은 점수로 돌려주고 질문 언어를
# 같게 판별한다(영어·한국어). 검색 경로를 새로 만들지 않고 같은 함수를 같은 순서로 부른다는 약속의 시험이다.
# HTTP 쪽의 검색 결과는 질문 기록(query_logs.retrieved_chunks)에서 읽는다. 두 언어의 청크가 모두 들어 있어,
# 다른 언어의 청크가 섞이면 결과가 달라진다. 설정 교체(dependency_overrides)는 client 픽스처가 시험이
# 끝날 때 비운다.
@pytest.mark.asyncio
@pytest.mark.parametrize("language", ["en", "ko"])
async def test_tool_returns_the_same_chunks_as_the_http_route(
    authed_client, db_session, session_factory, dense_settings, language
):
    app.dependency_overrides[get_settings] = lambda: dense_settings
    await _seed_both_languages(db_session)
    question = QUESTIONS[language]

    resp = await authed_client.post("/query/ask", json={"question": question, "top_k": 5})
    assert resp.status_code == 200
    log = await db_session.get(QueryLog, uuid.UUID(resp.json()["query_log_id"]))
    http_hits = [(chunk["chunk_id"], chunk["score"]) for chunk in log.retrieved_chunks]

    response = await search_docs(
        question, 5, session_factory=session_factory, embedder_for=lambda _language: FakeEmbeddingService()
    )

    tool_hits = [(hit.chunk_id, hit.score) for hit in response.hits]
    assert len(http_hits) == 2  # 시험이 빈 결과끼리 같은 것으로 통과하지 않게
    assert [chunk_id for chunk_id, _ in tool_hits] == [chunk_id for chunk_id, _ in http_hits]
    assert [score for _, score in tool_hits] == pytest.approx([score for _, score in http_hits])
    assert response.language == language
    assert [hit.rank for hit in response.hits] == [1, 2]
    assert [hit.content for hit in response.hits] == [
        f"best passage ({language})",
        f"other passage ({language})",
    ]


# 검색 도구는 질문 기록을 남기지 않는다(HTTP 경로와 달리). 도구를 부르기 전후 query_logs 행 수가 같고,
# 결과는 정말 검색됐다(청크가 있고 hits가 채워짐). MCP 결과의 모양(rank는 1부터, id는 uuid 글자, 필드
# 이름)도 함께 본다.
@pytest.mark.asyncio
async def test_search_writes_no_query_log(db_session, patched_search):
    fake = FakeEmbeddingService()
    await _add_chunk(
        db_session,
        "en",
        "path-params",
        "Path parameters use type hints.",
        fake.embed_query(QUESTIONS["en"]),
        "Tutorial > Path Parameters",
    )

    async def count_logs() -> int:
        return (await db_session.execute(text("SELECT count(*) FROM query_logs"))).scalar_one()

    before = await count_logs()
    async with _connected_client() as client:
        result = await client.call_tool(TOOL, {"question": QUESTIONS["en"], "top_k": 3})
    after = await count_logs()

    assert result.is_error is False
    hits = result.structured_content["hits"]
    assert len(hits) == 1
    assert set(hits[0]) == {
        "rank",
        "chunk_id",
        "document_id",
        "source_path",
        "heading_path",
        "score",
        "content",
    }
    assert hits[0]["rank"] == 1
    assert uuid.UUID(hits[0]["chunk_id"]) and uuid.UUID(hits[0]["document_id"])
    assert hits[0]["source_path"] == "docs/en/docs/path-params.md"
    assert hits[0]["heading_path"] == "Tutorial > Path Parameters"
    assert hits[0]["content"] == "Path parameters use type hints."
    assert result.structured_content["language"] == "en"
    assert result.structured_content["retrieval_mode"] == "dense"
    assert before == after == 0


# 검색 세션은 쓰기를 거절한다. MCP의 읽기 전용 표시는 힌트일 뿐 SDK가 막아 주지 않으므로, 서버 코드가 첫
# 문장으로 SET TRANSACTION READ ONLY를 보내 DB가 막게 한다. 그 안에서 INSERT를 보내면 'read-only
# transaction' 오류가 나고, 나간 뒤 새 세션에서 행 수는 그대로다.
@pytest.mark.asyncio
async def test_search_session_refuses_writes(session_factory):
    insert = text(
        "INSERT INTO documents (source_path, source_commit_sha, content_hash) "
        "VALUES ('docs/en/docs/x.md', 'deadbeef', 'hash-x')"
    )

    async with read_only_session(session_factory) as db:
        with pytest.raises(DBAPIError) as raised:
            await db.execute(insert)

    assert "read-only transaction" in str(raised.value)
    async with session_factory() as fresh:
        assert (await fresh.execute(text("SELECT count(*) FROM documents"))).scalar_one() == 0


# 검색이 건 정확 탐색 고정(SET LOCAL enable_indexscan = off)은 읽기 전용 세션을 나갈 때 풀린다. retrieve()는
# commit도 rollback도 하지 않으므로 부른 쪽이 트랜잭션을 끝내야 하는데, 세션이 나갈 때 rollback한다. 연결이
# 하나뿐인 풀에서 세션을 나간 뒤 이어서 연 새 세션은 같은 연결(같은 백엔드 프로세스)을 받으므로, 거기서 on이
# 보이면 고정이 다음 일에 번지지 않은 것이다.
@pytest.mark.asyncio
async def test_read_only_session_ends_the_exact_search_pin(db_engine, db_session):
    fake = FakeEmbeddingService()
    question = QUESTIONS["en"]
    await _add_chunk(
        db_session, "en", "path-params", "Path parameters use type hints.", fake.embed_query(question)
    )
    one_connection = create_async_engine(db_engine.url, pool_size=1, max_overflow=0, pool_timeout=10)
    factory = async_sessionmaker(one_connection, expire_on_commit=False)

    try:
        async with read_only_session(factory) as db:
            found = await retrieve(db, question, fake.embed_query(question), 5, "dense", language="en")
            pinned = (await db.execute(text("SHOW enable_indexscan"))).scalar()
            read_only = (await db.execute(text("SHOW transaction_read_only"))).scalar()
            backend_inside = (await db.execute(text("SELECT pg_backend_pid()"))).scalar()
        async with factory() as fresh:
            after = (await fresh.execute(text("SHOW enable_indexscan"))).scalar()
            backend_after = (await fresh.execute(text("SELECT pg_backend_pid()"))).scalar()
    finally:
        await one_connection.dispose()

    assert len(found) == 1
    assert backend_after == backend_inside  # 같은 연결을 이어 받았으니 'on'이 우연이 아니다
    assert (pinned, read_only, after) == ("off", "on", "on")


# 잘못된 입력은 DB 일을 하기 전에 거절한다: 오류 결과가 오고 세션 팩토리는 한 번도 불리지 않는다. 오류 글은
# '필드: 메시지' 한 줄이고 보낸 값은 담기지 않는다. 지원하지 않는 language는 SDK의 스키마 검증이 먼저
# 거절한다. 열: (보낸 인자, 오류 글에 있어야 하는 조각).
INVALID_INPUTS = [
    pytest.param({"question": ""}, "question: String should have at least 1 character", id="empty-question"),
    pytest.param(
        {"question": "x" * 2001},
        "question: String should have at most 2000 characters",
        id="question-2001-chars",
    ),
    pytest.param(
        {"question": "What is\x00FastAPI?"},
        "question: Value error, must not contain the NUL character (U+0000)",
        id="nul-in-question",
    ),
    pytest.param(
        {"question": "What is FastAPI?", "top_k": 0},
        "top_k: Input should be greater than or equal to 1",
        id="top-k-0",
    ),
    pytest.param(
        {"question": "What is FastAPI?", "top_k": 11},
        "top_k: Input should be less than or equal to 10",
        id="top-k-11",
    ),
    pytest.param({"question": "What is FastAPI?", "language": "jp"}, "language", id="unsupported-language"),
]


@pytest.mark.asyncio
@pytest.mark.parametrize(("arguments", "expected"), INVALID_INPUTS)
async def test_invalid_input_is_refused_before_any_database_work(
    monkeypatch, dense_settings, arguments, expected
):
    spy = SessionFactorySpy()
    monkeypatch.setattr(mcp_server, "async_session_maker", spy)
    monkeypatch.setattr(mcp_server, "get_embedding_service", lambda _language: FakeEmbeddingService())

    async with _connected_client() as client:
        result = await client.call_tool(TOOL, arguments)

    assert result.is_error is True
    assert expected in _text(result)
    assert "xxxxxxxxxx" not in _text(result)  # 보낸 2001자 질문을 오류 글에 되돌려 주지 않는다
    assert spy.calls == 0


# search_docs를 직접 부를 때는 검증 실패가 pydantic.ValidationError 그대로 올라온다(도구가 이것을 짧은
# 오류로 옮긴다). 검증은 DB 일보다 앞이라 세션 팩토리는 불리지 않는다.
@pytest.mark.asyncio
async def test_search_docs_lets_the_validation_error_through():
    spy = SessionFactorySpy()

    with pytest.raises(ValidationError) as raised:
        await search_docs("", session_factory=spy, embedder_for=lambda _language: FakeEmbeddingService())

    assert [error["loc"] for error in raised.value.errors()] == [("question",)]
    assert spy.calls == 0


# DB가 꺼져 있거나 닿지 않을 때(엔진 주소의 비밀번호와 주소는 오류에도 로그에도 나오면 안 된다): 도구는 정한
# 짧은 오류만 돌려준다. 접속이 거절되지 않고 묵살되는 환경에서도 시험이 오래 걸리지 않도록 접속 제한 시간을
# 3초로 준다. 실패 뒤 팩토리를 시험 DB 것으로 되돌려 같은 서버에 다시 부르면 성공한다(서버가 살아 있다).
@pytest.mark.asyncio
async def test_database_down_returns_a_short_error_without_the_url(
    monkeypatch, db_session, session_factory, dense_settings, caplog
):
    fake = FakeEmbeddingService()
    await _add_chunk(
        db_session, "en", "path-params", "Path parameters use type hints.", fake.embed_query(QUESTIONS["en"])
    )
    monkeypatch.setattr(mcp_server, "get_embedding_service", lambda _language: FakeEmbeddingService())
    dead_engine = create_async_engine(
        "postgresql+asyncpg://nobody:SECRET-PW@127.0.0.1:1/none", connect_args={"timeout": 3}
    )
    dead_factory = async_sessionmaker(dead_engine, expire_on_commit=False)
    monkeypatch.setattr(mcp_server, "async_session_maker", dead_factory)

    try:
        with caplog.at_level(logging.INFO):
            async with _connected_client() as client:
                failed = await client.call_tool(TOOL, {"question": QUESTIONS["en"]})
                monkeypatch.setattr(mcp_server, "async_session_maker", session_factory)
                recovered = await client.call_tool(TOOL, {"question": QUESTIONS["en"]})
    finally:
        await dead_engine.dispose()

    assert failed.is_error is True
    assert DATABASE_ERROR in _text(failed)
    for secret in ("SECRET-PW", "127.0.0.1:1", "127.0.0.1", "nobody"):
        assert secret not in _text(failed)
        assert secret not in caplog.text
    assert re.search(r"mcp search failed stage=database error=\w+", caplog.text)
    assert recovered.is_error is False
    assert len(recovered.structured_content["hits"]) == 1


# 청크가 하나도 없는 DB에서는 오류가 아니라 빈 결과다(문서가 다루지 않는 질문에 근거를 붙이지 않는 것이
# 검색의 설계다. 점수 바닥값 아래의 결과는 버려진다).
@pytest.mark.asyncio
async def test_empty_corpus_returns_no_hits_not_an_error(patched_search):
    async with _connected_client() as client:
        result = await client.call_tool(TOOL, {"question": QUESTIONS["en"]})

    assert result.is_error is False
    assert result.structured_content["hits"] == []


# 접속은 닿았는데 서버가 거절하는 경우(여기서는 없는 DB 이름. 틀린 비밀번호도 같은 갈래다)도 DB 구간의
# 실패다. SQLAlchemy는 접속 단계의 asyncpg 예외를 자기 예외로 바꾸지 않고 그대로 올리므로, 도구가 그것을
# 가려내지 않으면 클라이언트는 도구 이름만 든 오류를 받고 서버 로그에는 예외 글이 traceback과 함께 남는다.
# 정한 짧은 오류가 오고, 로그에는 예외의 종류 이름만 남는다(DB 이름이 든 예외 글은 남지 않는다).
@pytest.mark.asyncio
async def test_database_that_refuses_the_connection_is_a_database_failure(
    monkeypatch, db_engine, dense_settings, caplog
):
    missing = "no_such_database_for_this_test"
    refusing_engine = create_async_engine(db_engine.url.set(database=missing))
    refusing_factory = async_sessionmaker(refusing_engine, expire_on_commit=False)
    monkeypatch.setattr(mcp_server, "async_session_maker", refusing_factory)
    monkeypatch.setattr(mcp_server, "get_embedding_service", lambda _language: FakeEmbeddingService())

    try:
        with caplog.at_level(logging.INFO):
            async with _connected_client() as client:
                result = await client.call_tool(TOOL, {"question": QUESTIONS["en"]})
    finally:
        await refusing_engine.dispose()

    assert result.is_error is True
    assert DATABASE_ERROR in _text(result)
    assert missing not in _text(result)
    assert missing not in caplog.text
    assert "mcp search failed stage=database error=InvalidCatalogNameError" in caplog.text


# 질문 언어가 임베딩 모델과 재정렬기를 고른다: 한국어 질문이면 두 조회 모두 ko로 불린다(rerank 모드). 조회가
# 받은 언어를 무시하고 늘 같은 모델을 돌려주면 오류 없이 검색 품질만 조용히 떨어지므로(두 언어의 벡터는 서로
# 다른 공간이다), 가짜 조회가 받은 언어를 적어 두고 확인한다.
@pytest.mark.asyncio
async def test_the_question_language_picks_the_embedder_and_the_reranker(db_session, session_factory):
    fake = FakeEmbeddingService()
    question = QUESTIONS["ko"]
    passage = "경로 매개변수는 타입 힌트로 선언한다."
    await _add_chunk(db_session, "ko", "path-params", passage, fake.embed_query(question))
    asked: list[tuple[str, str]] = []

    def embedder_for(language):
        asked.append(("embedding", language))
        return FakeEmbeddingService()

    def reranker_for(language):
        asked.append(("reranking", language))
        return KeywordReranker("경로")

    response = await search_docs(
        question,
        5,
        session_factory=session_factory,
        embedder_for=embedder_for,
        reranker_for=reranker_for,
        settings=get_settings().model_copy(update={"retrieval_mode": "rerank"}),
    )

    assert asked == [("embedding", "ko"), ("reranking", "ko")]
    assert response.language == "ko"
    assert [hit.content for hit in response.hits] == [passage]


# language를 지정하면 질문에서 판별한 언어를 이긴다(도구 설명이 모델에게 약속한 'set language to override the
# detection'). 영어 질문을 language="ko"로 부르면 한국어 모델로 임베딩해 한국어 청크에서만 찾고, 응답의
# language도 ko다. 지정을 무시하고 질문에서 판별하면 영어 모델로 영어 청크를 찾게 된다.
@pytest.mark.asyncio
async def test_the_language_argument_overrides_the_detection(
    monkeypatch, db_session, session_factory, dense_settings
):
    await _seed_both_languages(db_session)
    asked: list[str] = []

    def embedder_for(language):
        asked.append(language)
        return FakeEmbeddingService()

    monkeypatch.setattr(mcp_server, "async_session_maker", session_factory)
    monkeypatch.setattr(mcp_server, "get_embedding_service", embedder_for)

    async with _connected_client() as client:
        result = await client.call_tool(TOOL, {"question": QUESTIONS["en"], "language": "ko"})

    assert result.is_error is False
    assert asked == ["ko"]
    assert result.structured_content["language"] == "ko"
    paths = [hit["source_path"] for hit in result.structured_content["hits"]]
    assert len(paths) == 2
    assert all(path.startswith("docs/ko/") for path in paths)


# 질문을 임베딩한 모델의 점수 바닥값이 검색에 쓰인다(HTTP 경로의 tests/test_query.py와 같은 확인). 코사인
# 0.25인 청크는 공통 바닥값 0.3에서는 잘려 결과가 비고, 그 모델의 바닥값을 0.2로 넣으면(SCORE_FLOORS,
# monkeypatch가 시험 뒤에 되돌림) 나온다. 도구가 score_floor를 넘기지 않으면 모델별 바닥값이 무시되어 둘째
# 호출도 빈 결과가 된다.
@pytest.mark.asyncio
async def test_search_uses_the_score_floor_of_the_embedding_model(
    monkeypatch, db_session, session_factory, dense_settings
):
    await _add_chunk(
        db_session,
        "en",
        "body",
        "Declare a Pydantic model.",
        # 단위 벡터를 유지하도록 둘째 성분을 sqrt(1 − 0.25²)로 둔다. 첫 성분 0.25가 곧 질문 벡터와의
        # 코사인이다.
        [0.25, (1 - 0.25**2) ** 0.5] + [0.0] * (EMBEDDING_DIM - 2),
    )
    common = {
        "session_factory": session_factory,
        "embedder_for": lambda _language: AxisEmbeddingService(),
        "settings": dense_settings,
    }

    under_shared_floor = await search_docs("Body?", **common)
    monkeypatch.setitem(retrieval.SCORE_FLOORS, "axis-embedding", 0.2)
    under_model_floor = await search_docs("Body?", **common)

    assert under_shared_floor.hits == []
    assert [hit.source_path for hit in under_model_floor.hits] == ["docs/en/docs/body.md"]
    assert under_model_floor.hits[0].score == pytest.approx(0.25)


# 첫 질문 둘이 동시에 와도 모델을 올리는 일은 한 번에 하나만 돈다. 서비스 모듈의 캐시에는 잠금이 없어, 줄
# 세우지 않으면 두 스레드가 같은 모델을 각각 올린다(시간과 메모리가 두 배). 서비스 모듈의 함수를 '안에 들어와
# 있는 스레드 수를 세는' 느린 대역으로 바꾸고 두 스레드에서 동시에 불러, 겹쳐 들어온 적이 없는지 본다.
def test_model_lookups_run_one_at_a_time(monkeypatch):
    from app.services import embedding

    counter_guard = threading.Lock()
    inside = 0
    most_inside = 0

    def slow_lookup(language):
        nonlocal inside, most_inside
        with counter_guard:
            inside += 1
            most_inside = max(most_inside, inside)
        time.sleep(0.2)
        with counter_guard:
            inside -= 1
        return language

    monkeypatch.setattr(embedding, "get_embedding_service", slow_lookup)
    threads = [
        threading.Thread(target=mcp_server.get_embedding_service, args=(language,))
        for language in ("en", "ko")
    ]

    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=10)

    assert not any(thread.is_alive() for thread in threads)
    assert most_inside == 1


# rerank 모드에서는 그 질문 언어의 재정렬기(reranker_for(언어))를 검색에 넘기고, 결과 순서가 재정렬 점수를
# 따른다. dense 모드에서는 reranker_for를 부르지 않는다(불리면 실패하는 함수로 확인). 같은 두 청크를
# dense로는 질문과 같은 벡터의 청크가 먼저, rerank로는 키워드가 든 청크가 먼저 나오게 놓아 두 모드의 차이가
# 시험에 드러나게 한다.
@pytest.mark.asyncio
async def test_rerank_mode_passes_the_language_reranker(db_session, session_factory):
    fake = FakeEmbeddingService()
    question = "How do I share logic?"
    close = "Dependencies are declared with Depends."
    keyword = "Environment variables are read with settings."
    await _add_chunk(db_session, "en", "close", close, fake.embed_query(question))
    await _add_chunk(db_session, "en", "keyword", keyword, fake.embed_query("an unrelated sentence"))
    languages_asked: list[str] = []

    def reranker_for(language):
        languages_asked.append(language)
        return KeywordReranker("Environment")

    def reranker_that_must_not_be_asked(_language):
        raise AssertionError("reranker_for must not be called outside the rerank mode")

    common = {"session_factory": session_factory, "embedder_for": lambda _language: FakeEmbeddingService()}
    dense = get_settings().model_copy(update={"retrieval_mode": "dense"})
    rerank = get_settings().model_copy(update={"retrieval_mode": "rerank"})

    by_dense = await search_docs(
        question, 5, settings=dense, reranker_for=reranker_that_must_not_be_asked, **common
    )
    by_rerank = await search_docs(question, 5, settings=rerank, reranker_for=reranker_for, **common)

    assert by_dense.retrieval_mode == "dense"
    assert [hit.content for hit in by_dense.hits] == [close, keyword]
    assert by_rerank.retrieval_mode == "rerank"
    assert [hit.content for hit in by_rerank.hits] == [keyword, close]
    assert by_rerank.hits[0].score == 1.0
    assert languages_asked == ["en"]


# 서버는 나갈 때(클라이언트가 연결을 닫아 서버가 끝날 때) DB 엔진(풀의 연결)을 한 번 닫는다. 들어갈 때는
# 아무것도 닫지 않는다.
@pytest.mark.asyncio
async def test_the_engine_is_disposed_once_when_the_client_disconnects(monkeypatch):
    recorder = EngineRecorder()
    monkeypatch.setattr(db_session_module, "engine", recorder)

    async with _connected_client() as client:
        await client.list_tools()
        disposed_while_connected = recorder.disposed

    assert disposed_while_connected == 0
    assert recorder.disposed == 1


# 실제 stdio 전송으로 서버를 자식 프로세스로 띄운다(`python -m app.mcp_server`, 클라이언트가 하는 일과
# 같다). 도구 목록의 이름과 한글 제목이 그대로 오는지(자식에 -X utf8을 주지 않아도 UTF-8 왕복이 맞는지), 빈
# 질문은 오류 결과인지 본다. 모델과 DB 접속이 필요 없는 호출만 한다.
# 표준 출력이 깨끗한지는 호출이 성공했는지만으로는 알 수 없다. SDK 클라이언트는 프로토콜이 아닌 줄을
# 건너뛰고 계속 진행하며, 그 사실을 클라이언트 쪽 로거 mcp.client.stdio에 ERROR('Failed to parse JSONRPC
# message from server')로만 남긴다. 그래서 이 로거의 경고 이상 기록이 하나도 없었는지를 본다. 같은 로거는
# Client 블록을 나갈 때 자식을 끝내지 못해 포기했다는 경고도 남긴다('is still alive after the kill
# escalation'). 블록을 나가면 SDK가 자식의 표준 입력을 닫고 잠깐 기다린 뒤 끝나지 않으면 프로세스 트리를
# 끝내는데, 그렇게 끝낸 경우는 기록에 남지 않으므로 이 시험이 보는 것은 '자식이 남지 않았다'까지다(스스로
# 제때 끝났는지는 보지 않는다).
@pytest.mark.asyncio
async def test_stdio_server_lists_the_tool_and_keeps_stdout_clean(caplog):
    params = StdioServerParameters(
        command=sys.executable, args=["-m", "app.mcp_server"], env=_child_env(), cwd=REPO_ROOT
    )

    with caplog.at_level(logging.WARNING):
        with anyio.fail_after(CHILD_TIMEOUT_SECONDS):
            async with Client(params) as client:
                listing = await client.list_tools()
                refused = await client.call_tool(TOOL, {"question": ""})

    assert [tool.name for tool in listing.tools] == [TOOL]
    assert listing.tools[0].title == "FastAPI 문서 검색"
    assert refused.is_error is True
    client_problems = [
        record.getMessage()
        for record in caplog.records
        if record.name == "mcp.client.stdio" and record.levelno >= logging.WARNING
    ]
    assert client_problems == []


# HTTP 서비스(app.main)는 이 도구 모듈도 mcp 패키지도 불러오지 않는다. 서비스 이미지는 mcp 의존성 그룹 없이
# 만들어지므로(pyproject.toml), 서비스 코드가 이 모듈을 불러오는 순간 이미지가 시작하지 못한다. 서비스의
# 코드와 의존성이 도구를 더하기 전과 같게 남는다는 약속을 고정한다.
def test_service_app_does_not_import_the_mcp_tool():
    code = (
        "import sys\n"
        "import app.main\n"
        "loaded = sorted(name for name in sys.modules\n"
        "                if name in ('mcp', 'app.mcp_server') or name.startswith('mcp.'))\n"
        "assert not loaded, loaded[:10]\n"
    )

    done = subprocess.run(
        [sys.executable, "-c", code],
        cwd=REPO_ROOT,
        env=_child_env(),
        capture_output=True,
        timeout=CHILD_TIMEOUT_SECONDS,
    )

    assert done.returncode == 0, done.stderr.decode(errors="replace")

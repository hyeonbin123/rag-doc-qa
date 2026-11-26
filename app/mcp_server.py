# [파일 역할] 이 저장소의 FastAPI 문서 검색을 MCP 도구 search_fastapi_docs 하나로 내놓는 읽기 전용 MCP 서버.
# MCP 클라이언트(코딩 에이전트나 채팅 앱)가 `python -m app.mcp_server`를 자식 프로세스로 띄우면, 표준
# 입출력(stdio)으로 도구 목록을 알리고 질문을 받아 가장 관련 있는 문서 조각과 그 출처 경로를 돌려준다.
# [흐름] 입력 검증(AskRequest) → 질문 언어 판별 → 그 언어의 모델로 질문 임베딩(모델 스레드) → 읽기 전용
# 트랜잭션에서 retrieve() → SearchResponse. /query/ask(app/routers/query.py)가 답변을 만들기 앞에서 밟는
# 단계와 같은 함수를 같은 순서로 부른다. 답변 생성과 질문 기록(query_logs 테이블) 저장은 하지 않는다.
# [설계 이유]
# - HTTP 전송은 열지 않았다(stdio만). HTTP로 열면 인증·접근 통제와 보안 점검(docs/security-scan.md) 범위가
#   늘어난다. stdio는 클라이언트가 띄운 자식 프로세스와 부모 사이의 파이프라 새로 열리는 포트가 없다.
# - 기존 라우터와 서비스를 고치지 않고, 같은 서비스 함수(retrieve, detect_language, get_embedding_service
#   등)를 같은 순서로 부른다. 그래야 HTTP 서비스의 코드·의존성·경로가 도구를 더하기 전과 같게 남는다.
#   서비스(app.main)는 이 모듈을 불러오지 않고, 서비스 이미지는 mcp 의존성 그룹을 설치하지
#   않는다(pyproject.toml). tests/test_mcp_server.py가 이 경계를 고정한다.
# - 읽기 전용은 서버 코드가 직접 지킨다. MCP의 도구 주석(readOnlyHint 등)은 클라이언트에게 주는 힌트일 뿐
#   SDK가 쓰기를 막아 주지 않는다. 그래서 검색을 SET TRANSACTION READ ONLY로 연 트랜잭션에서 하고 나갈 때
#   rollback한다(read_only_session). 질문 기록 모델(app/models/query_log.py)은 불러오지도 않는다.
# - 표준 출력에는 아무것도 쓰지 않는다. stdio 서버의 표준 출력은 프로토콜 전용이다. SDK는 서비스를 시작하면
#   표준 출력을 표준 오류로 돌리지만 그 전에 쓴 글은 프로토콜에 섞이므로, print를 쓰지 않고 모듈을 불러올
#   때는 아무 일도 하지 않는다. 서버 객체(MCPServer 생성이 로깅을 설정한다)도 불러올 때가 아니라
#   build_server()가 만든다. 로그는 configure_logging()이 만드는 표준 오류 핸들러로만 남기고, 이 앱의 다른
#   로그처럼 영어 key=value 꼴로 쓴다(Windows에서 자식 프로세스의 표준 오류는 UTF-8 모드가 아니면 로캘
#   인코딩으로 나가므로, 한글 로그는 UTF-8로 읽는 클라이언트의 로그 창에서 깨질 수 있다).
# [주의]
# - 설정(DATABASE_URL 등)은 지금 작업 폴더의 .env에서 읽는다(app/config.py). stdio 클라이언트는 부모의 환경
#   변수를 거의 물려주지 않으므로(SDK가 정한 안전 목록만 간다) 클라이언트 설정에서 작업 폴더를 이 저장소
#   루트로 줘야 한다. 모델 캐시 위치를 HF_HOME으로 옮겨 둔 PC에서는 클라이언트 설정의 env에도 HF_HOME을
#   적어야 같은 캐시를 쓴다(안 적으면 기본 위치에 모델을 다시 내려받는다).
# - 모델과 모델 라이브러리(torch, sentence-transformers)는 첫 호출 때 올린다. 이 모듈을 불러오는 것만으로는
#   app/services/embedding.py와 reranking.py를 불러오지 않는다(아래 get_embedding_service·
#   get_reranker_service가 불릴 때 불러온다). 그 라이브러리를 불러오는 데만 10초 안팎이 걸려, 시작할 때
#   불러오면 서버가 뜨는 시간이 그만큼 늘고 클라이언트의 초기화 대기 시간을 넘길 수 있다. 그래서 서버는 몇
#   초 안에 뜨고, 대신 첫 질문이 라이브러리와 모델을 올리는 시간만큼 느리다.
# - mcp 패키지는 의존성 그룹 mcp에만 있다(`uv sync --group mcp`, 개발 환경에서는 dev 그룹이 함께 설치한다).
# [연결] 검색은 app/services/retrieval.py, 임베딩은 app/services/embedding.py(모델 스레드는
# app/services/inference.py), DB 세션은 app/db/session.py, 입력 검증은 app/schemas/query.py, 로깅은
# app/core/logging.py. 시험은 tests/test_mcp_server.py.

import logging
import threading
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Annotated, Literal

# asyncpg: DB 접속 단계에서 서버가 거절할 때(틀린 비밀번호, 없는 DB 이름, 기동 중) 나는 예외의 뿌리 둘을 DB
# 구간의 실패로 가려내는 데 쓴다. SQLAlchemy는 질의를 실행할 때의 asyncpg 예외만 자기 예외로 바꾸고, 접속할
# 때의 것은 그대로 올린다.
import asyncpg
from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations
from pydantic import BaseModel, Field, ValidationError

# text: 읽기 전용 트랜잭션을 여는 문장을 보낸다. SQLAlchemyError: DB 구간의 실패를 가려내는 데 쓴다.
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

# async_session_maker와 db_module: 같은 app/db/session.py에서 두 가지를 다른 방식으로 가져온다.
# async_session_maker는 이 모듈의 전역으로 두어 시험이 바꿔 끼울 수 있게 하고(검색 함수가 부를 때마다 이
# 전역을 읽는다), 서버가 나갈 때 닫는 engine은 모듈째 가져와 나갈 때 그 속성을 읽는다.
from app.config import Settings, get_settings
from app.core.logging import configure_logging
from app.db import session as db_module
from app.db.session import async_session_maker
from app.schemas.query import AskRequest
from app.services.inference import run_model
from app.services.language import Language, detect_language
from app.services.retrieval import RetrievalMode, retrieve, score_floor_for

# 임베딩·재정렬 서비스의 타입은 주석(타입 힌트)에만 쓴다. 두 모듈은 불러올 때 torch와 sentence-transformers를
# 끌어와 10초 안팎이 걸리므로 여기서 불러오지 않고, 아래 get_embedding_service·get_reranker_service가 처음
# 불릴 때 불러온다(파일 머리의 [주의]).
if TYPE_CHECKING:
    from app.services.embedding import EmbeddingService
    from app.services.reranking import RerankerService

# MCP 서버 이름. 클라이언트가 서버를 알아보는 이름이다.
SERVER_NAME = "rag-doc-qa"

# 서버 안내문(instructions). 모델에게 가는 글이라 정한 영어 문안 그대로 둔다. MCP 클라이언트는 이 글을
# 서버의 사용법으로 모델에게 보여 줄 수 있다. 도구가 하나뿐이라 짧게 두고, 근거를 쓸 때 출처
# 경로(source_path)를 밝히라고 알린다.
SERVER_INSTRUCTIONS = (
    "Read-only search over the FastAPI documentation corpus of this project. "
    "Call search_fastapi_docs to find passages, and cite source_path when you use them."
)

# 도구 설명. 모델에게 가는 글이라 정한 영어 문안 그대로 둔다. 읽는 모델이 알아야 할 것을 담았다: 읽기
# 전용이라는 것(답을 만들지도 질문을 저장하지도 않는다), 질문 언어에 따라 영어 원문 또는 한국어 번역에서
# 찾는다는 것, 그리고 결과는 순위일 뿐 '문서가 이 질문을 다룬다'는 확인이 아니라는 것. 끝의 두 문장에
# 검색 모드를 적지 않은 까닭: 점수 바닥값(app/services/retrieval.py의 SCORE_FLOOR) 아래를 버리는 것은 dense
# 검색인데, hybrid·rerank도 질문에 검색할 단어가 없으면(예: 한글만 있는 질문) dense로 대신하므로 '어느
# 모드에서 결과가 비는가'를 한 문장으로 맞게 적을 수 없다. 모드와 무관하게 맞는 것만 적는다: 문서가 다루지
# 않는 질문에도 약하게 관련된 조각이 올 수 있고(dense에서는 바닥값을 겨우 넘는 조각, hybrid·rerank에서는
# 어휘로만 걸린 낮은 점수의 조각), 결과가 빌 수도 있다. 그래서 읽는 모델이 '결과가 있으면 문서가 다룬다'로
# 거꾸로 읽지 않게 내용을 확인하라고 적는다.
# 함수의 docstring이 아니라 상수로 두고 add_tool(description=...)로 넘기는 까닭: SDK는 함수의 __doc__를
# 줄바꿈과 들여쓰기까지 그대로 도구 설명으로 보낸다. 여러 줄 docstring이면 설명에 줄바꿈과 공백이 섞여
# 나간다. 상수는 한 문단 그대로 나간다.
TOOL_DESCRIPTION = (
    "Search the FastAPI documentation (English originals and Korean translations) and return the most "
    "relevant passages with their source paths. Read-only: it runs the same retrieval as this project's "
    "HTTP API (question language detection, same-language embedding, RETRIEVAL_MODE search) and neither "
    "generates an answer nor stores the question. Ask in English to search the English docs or in Korean "
    "to search the Korean translations; set language to override the detection. Results are ranked, not "
    "verified: a question the docs do not cover can still return weakly related passages, and the hits "
    "list can also be empty. Check the content before relying on a hit."
)

# 도구가 클라이언트(모델)에게 돌려주는 짧은 오류 글. 모델에게 가는 글이라 정한 영어 문안 그대로 둔다. 어떤
# 구간이 왜 안 됐는지와 무엇을 하면 되는지만 담고, DB 주소(비밀번호가 들어 있다)·예외 글·경로는 싣지 않는다.
# - DATABASE_ERROR: DB 구간의 실패 전부에 쓴다. 접속이 안 되는 경우뿐 아니라 접속은 됐는데 질의가 실패한
#   경우(예: 마이그레이션을 하지 않아 테이블이 없음)도 여기로 오므로 '닿지 못했다'가 아니라 '질의하지
#   못했다'고 적고, 확인할 것 둘(떠 있는지, 마이그레이션을 했는지)을 알린다.
# - EMBEDDING_ERROR: 모델 구간의 실패 전부에 쓴다. rerank 모드에서는 재정렬 모델을 올리다 난 실패도 여기로
#   오므로 두 모델을 함께 적는다.
DATABASE_ERROR = (
    "The document database could not be queried. Check that it is running and migrated, then try again."
)
EMBEDDING_ERROR = (
    "The embedding or reranking model could not be loaded or run. "
    "Check the model cache (HF_HOME) and the network."
)

# 읽기 전용 트랜잭션을 여는 문장. 트랜잭션의 첫 문장으로 보내, 그 트랜잭션의 어떤 문장도 쓰기 모드로 돌지
# 않게 한다. SET TRANSACTION은 트랜잭션 안에서만 효과가 있다. 앱의 세션(app/db/session.py)은 첫 문장에서
# 트랜잭션을 여므로(autobegin) 이 문장이 그 트랜잭션에 걸리지만, AUTOCOMMIT 연결이면 PostgreSQL이 경고만
# 내고 아무 효과가 없다. 그래서 세션 팩토리를 AUTOCOMMIT으로 바꾸면 안 된다.
READ_ONLY_SQL = "SET TRANSACTION READ ONLY"

# 이 모듈의 로그. __name__ 대신 이름을 직접 쓰는 까닭: `python -m app.mcp_server`로 실행하면 __name__이
# '__main__'이 되어 로그에 모듈 이름이 제대로 찍히지 않는다. configure_logging()의 형식으로 'app.mcp_server'
# 이름이 찍힌다.
logger = logging.getLogger("app.mcp_server")


# 언어에 맞는 임베딩 서비스를 돌려준다. app/services/embedding.py의 같은 이름 함수를 **불릴 때** 불러와
# 그대로 부르는 얇은 포장이다.
# - 왜 포장하나: 그 모듈은 불러올 때 torch와 sentence-transformers를 끌어와 10초 안팎이 걸린다. 모듈 맨 위에서
#   불러오면 서버가 뜨는 시간이 그만큼 늘어 클라이언트의 초기화 대기 시간을 넘길 수 있다. 여기서 불러오면
#   그 시간이 첫 질문으로 옮겨 가고, search_docs가 이 함수를 모델 스레드(run_model)에서 부르므로 불러오는
#   동안 이벤트 루프도 막히지 않는다.
# - 돌려주는 것은 HTTP 경로가 쓰는 것과 같은 서비스다(모델 이름별로 한 번만 만들어 재사용한다).
# - search_docs는 embedder_for가 None일 때 이 모듈의 전역 이름으로 이 함수를 찾는다(시험이 바꿔 끼운다).
# - _model_load_lock: 첫 질문 둘이 동시에 오면 모델 스레드 둘이 같은 모델을 각각 올린다(서비스 모듈의
#   캐시에는 잠금이 없다. HTTP 서비스는 시작할 때 차례로 올려 두므로 겪지 않는다). 올리는 일을 한 번에
#   하나로 줄 세우면 둘째 호출은 첫째가 올린 것을 캐시에서 받는다. 라이브러리를 불러오는 일도 같은 잠금
#   안이라 두 스레드가 동시에 불러오다 한쪽이 실패하는 일이 없다. 이미 올라온 뒤에는 잠금 안에서 캐시를
#   읽고 곧바로 돌아온다.
_model_load_lock = threading.Lock()


def get_embedding_service(language: Language) -> "EmbeddingService":
    with _model_load_lock:
        from app.services.embedding import get_embedding_service as load_embedding_service

        return load_embedding_service(language)


# 언어에 맞는 재정렬 서비스를 돌려준다(rerank 모드에서만 불린다). get_embedding_service와 같은 까닭으로
# app/services/reranking.py를 불릴 때 불러오고, 같은 잠금으로 줄 세운다.
def get_reranker_service(language: Language) -> "RerankerService":
    with _model_load_lock:
        from app.services.reranking import get_reranker_service as load_reranker_service

        return load_reranker_service(language)


# 검색 결과 한 건. 도구의 구조화된 결과(structuredContent)와 출력 스키마(outputSchema)가 된다. 모델이 읽는
# 글이라 클래스에 docstring을 달지 않는다(pydantic은 클래스 docstring을 스키마의 description으로 내보낸다).
# 필드 설명은 아래 주석에 있다.
# - rank: 검색 순서(1부터).
# - chunk_id·document_id: uuid 글자.
# - source_path: 저장소 안 문서 경로(예: docs/ko/docs/tutorial/body.md). 근거를 쓸 때 출처로 밝힌다.
# - heading_path: '페이지 제목 > 절 > 소절' 꼴의 위치. 없을 수 있다.
# - score: 뜻은 검색 모드를 따른다(dense·hybrid는 코사인 유사도, rerank는 재정렬 모델의 관련도 확률).
# - content: 문서 조각의 본문.
class SearchHit(BaseModel):
    rank: int
    chunk_id: str
    document_id: str
    source_path: str
    heading_path: str | None
    score: float
    content: str


# 검색 결과 전체. language는 실제로 검색한 문서 언어(질문에서 판별했거나 호출이 지정한 값)이고,
# retrieval_mode는 서버 설정 RETRIEVAL_MODE다. 결과가 없으면 hits가 빈 목록이다(오류가 아니다).
class SearchResponse(BaseModel):
    language: Language
    retrieval_mode: RetrievalMode
    hits: list[SearchHit]


# 질문을 임베딩하는 구간(모델 올리기와 계산, rerank 모드에서는 재정렬 모델 올리기까지)의 실패. 원인 예외는
# __cause__에 있다. DB 구간의 실패(DatabaseUnavailable)와 구별하려고 따로 둔다: 모델 캐시가 없고 네트워크도
# 없을 때의 OSError가 'DB에 닿지 못함'으로 보이면 안 된다.
class EmbeddingUnavailable(Exception):
    pass


# DB 구간(세션 열기부터 retrieve()까지)의 실패. 원인 예외는 __cause__에 있다. 예외 글에는 DB 주소(비밀번호
# 포함)가 들어갈 수 있으므로 이 예외는 글 없이 올리고, 로그에는 원인의 종류 이름만 남긴다.
class DatabaseUnavailable(Exception):
    pass


# 검색용 읽기 전용 DB 세션. 세션을 열어 첫 문장으로 SET TRANSACTION READ ONLY를 보내고, 나갈 때
# rollback한다.
# - 이 트랜잭션 안에서는 INSERT·UPDATE·DELETE·DDL이 'cannot execute ... in a read-only transaction' 오류로
#   거절된다. 검색은 SELECT와 SET LOCAL(정확 탐색 고정)만 보내므로 이것과 함께 쓸 수 있다.
# - rollback이 필요한 까닭: retrieve()는 commit도 rollback도 하지 않아서 부른 쪽이 트랜잭션을 끝내야 정확
#   탐색 고정(SET LOCAL enable_indexscan = off, app/services/retrieval.py의 pin_exact_dense_search)이
#   풀린다. 풀에 돌려준 연결이 고정을 품은 채 다음 일에 쓰이면 안 된다. 읽기만 했으므로 commit이 아니라
#   rollback이다.
# - session_factory가 None이면 부를 때 이 모듈의 전역 async_session_maker를 쓴다(기본값으로 묶어 두지
#   않는다. 시험이 전역을 바꿔 끼운다).
@asynccontextmanager
async def read_only_session(
    session_factory: Callable[[], AsyncSession] | None = None,
) -> AsyncIterator[AsyncSession]:
    factory = session_factory if session_factory is not None else async_session_maker
    async with factory() as session:
        try:
            await session.execute(text(READ_ONLY_SQL))
            yield session
        finally:
            await session.rollback()


# 질문 하나로 문서를 검색한다(도구 본문의 알맹이). /query/ask와 같은 순서로 같은 함수를 부른다.
# - 입력 검증: AskRequest로 검증한다(실패는 pydantic.ValidationError 그대로 올린다).
# - 언어: language가 auto면 질문에 한글이 있을 때 ko, 아니면 en. 지정했으면 그 값.
# - 모델 구간: 그 언어의 임베딩 모델을 올리고 질문을 임베딩한다. 둘 다 CPU를 쓰는 동기 호출이라 모델
#   스레드(run_model)에서 돌린다. 특히 첫 호출에서 모델 라이브러리를 불러오고 모델을 올리는 동안(십몇 초)
#   이벤트 루프를 막지 않으려는 것이다.
#   rerank 모드면 재정렬 모델도 여기서, DB 세션을 열기 전에 올린다(모델을 올리는 동안 DB 트랜잭션을 쥐고
#   있지 않으려고. 그리고 재정렬 모델을 못 올린 실패가 DB 실패로 보이지 않게). 이 구간의 실패는
#   EmbeddingUnavailable로 올린다(이름은 임베딩이지만 재정렬 모델의 실패도 담는다).
# - DB 구간: 읽기 전용 세션에서 retrieve()를 부른다. 인자의 이름과 순서는 app/routers/query.py의 호출과
#   같다. 이 구간의 SQLAlchemyError, asyncpg의 PostgresError·InterfaceError, OSError·TimeoutError는
#   DatabaseUnavailable로 올린다. 그 밖의 예외(코드의 버그 등)는 그대로 올린다.
# - 두 구간의 실패는 원인 예외를 __cause__로 달고, 로그에는 종류 이름만 남긴다(예외 글에는 DB 주소나 경로가
#   들어갈 수 있다).
# - 검색 결과가 없으면 오류가 아니라 hits가 빈 SearchResponse다.
# - 키워드 인자가 None이면 부를 때 이 모듈의 전역(async_session_maker, get_embedding_service,
#   get_reranker_service, get_settings())을 쓴다. 기본값으로 묶어 두면 시험이 monkeypatch로 바꿔 끼울
#   수 없다.
async def search_docs(
    question: str,
    top_k: int = 5,
    language: str = "auto",
    *,
    session_factory: Callable[[], AsyncSession] | None = None,
    embedder_for: "Callable[[Language], EmbeddingService] | None" = None,
    reranker_for: "Callable[[Language], RerankerService] | None" = None,
    settings: Settings | None = None,
) -> SearchResponse:
    request = AskRequest(question=question, top_k=top_k, language=language)
    settings = settings if settings is not None else get_settings()
    embedder_lookup = embedder_for if embedder_for is not None else get_embedding_service
    reranker_lookup = reranker_for if reranker_for is not None else get_reranker_service
    mode = settings.retrieval_mode
    lang: Language = detect_language(request.question) if request.language == "auto" else request.language

    # 모델 구간. 어떤 예외든(캐시 없음, 허브 오류, 표에 없는 모델, torch 오류 등 갈래가 많다) 이 구간의
    # 실패는 같은 오류로 옮기고, 종류 이름은 로그에 남는다.
    try:
        embedder = await run_model(embedder_lookup, lang)
        query_embedding = await run_model(embedder.embed_query, request.question)
        reranker = await run_model(reranker_lookup, lang) if mode == "rerank" else None
    except Exception as exc:
        logger.warning("mcp search failed stage=embedding error=%s", type(exc).__name__)
        raise EmbeddingUnavailable from exc

    # DB 구간. SQLAlchemyError는 질의 실행의 실패(테이블 없음 등), asyncpg의 두 뿌리 예외는 접속 단계에서
    # 서버가 거절한 경우(틀린 비밀번호, 없는 DB 이름, 기동 중)와 연결 자체의 오류, OSError는 접속 거절·이름
    # 풀이 실패다. TimeoutError는 OSError의 하위 클래스이지만 접속 시간 초과를 일부러 드러내려고 따로 적는다.
    try:
        async with read_only_session(session_factory) as db:
            retrieved = await retrieve(
                db,
                request.question,
                query_embedding,
                request.top_k,
                mode,
                language=lang,
                reranker=reranker,
                score_floor=score_floor_for(embedder.model_name),
            )
    except (SQLAlchemyError, asyncpg.PostgresError, asyncpg.InterfaceError, OSError, TimeoutError) as exc:
        logger.warning("mcp search failed stage=database error=%s", type(exc).__name__)
        raise DatabaseUnavailable from exc

    hits = [
        SearchHit(
            rank=rank,
            chunk_id=str(chunk.chunk_id),
            document_id=str(chunk.document_id),
            source_path=chunk.source_path,
            heading_path=chunk.heading_path,
            score=chunk.score,
            content=chunk.content,
        )
        for rank, chunk in enumerate(retrieved, start=1)
    ]
    return SearchResponse(language=lang, retrieval_mode=mode, hits=hits)


# pydantic 검증 오류를 '필드: 메시지' 한 줄(여러 개면 '; '로 이음)로 줄인다. 예: `question: String should
# have at most 2000 characters`. 보낸 값(input)은 싣지 않는다. 모델이 읽고 고쳐 다시 부를 수 있을 만큼만
# 알리고, 질문 글을 오류와 서버 로그에 되돌려 싣지 않으려는 것이다.
def _validation_summary(error: ValidationError) -> str:
    parts = []
    for item in error.errors(include_url=False, include_context=False, include_input=False):
        field = ".".join(str(part) for part in item["loc"])
        parts.append(f"{field}: {item['msg']}" if field else item["msg"])
    return "; ".join(parts)


# 도구 본문. 모듈 수준의 보통 함수이고 등록은 build_server()가 한다. search_docs를 부르고 그 예외를
# 클라이언트에게 갈 짧은 오류(ToolError)로 옮긴다.
# - ValidationError → 필드와 메시지 한 줄. 입력을 고쳐 다시 부르면 된다.
# - DatabaseUnavailable → DATABASE_ERROR, EmbeddingUnavailable → EMBEDDING_ERROR. 두 구간의 오류 글을 섞지
#   않는다.
# - 그 밖의 예외는 옮기지 않고 그대로 올린다. SDK가 클라이언트에는 도구 이름만 든 오류를 주고 서버의 표준
#   오류에 traceback을 남긴다(예외 글이 클라이언트에 가지 않는다).
# 인자 설명(아래 Field의 description)은 모델에게 가는 글이라 정한 영어 문안 그대로 둔다. 도구 설명은
# TOOL_DESCRIPTION이고, 이 함수에는 docstring을 달지 않는다(add_tool에 description을 주면 docstring은 쓰이지
# 않으므로, 달아 두면 어느 글이 모델에게 가는지 헷갈린다).
# 인자의 범위(질문 1~2000자, top_k 1~10)는 여기서 스키마로 걸지 않고 search_docs의 AskRequest 검증에 맡긴다.
# 스키마로 걸면 SDK가 먼저 거절하는데 그 오류 글에는 보낸 값이 그대로 실리고, AskRequest 검증은
# '필드: 메시지' 한 줄만 돌려주기 때문이다. 범위는 인자 설명에 적혀 있다.
async def search_fastapi_docs(
    question: Annotated[str, Field(description="The question to search for (1-2000 characters).")],
    top_k: Annotated[int, Field(description="How many passages to return (1-10).")] = 5,
    language: Annotated[
        Literal["auto", "en", "ko"],
        Field(
            description=(
                "Which translation to search: auto picks Korean when the question contains Hangul, "
                "otherwise English."
            )
        ),
    ] = "auto",
) -> SearchResponse:
    try:
        return await search_docs(question, top_k, language)
    except ValidationError as exc:
        raise ToolError(_validation_summary(exc)) from exc
    except EmbeddingUnavailable as exc:
        raise ToolError(EMBEDDING_ERROR) from exc
    except DatabaseUnavailable as exc:
        raise ToolError(DATABASE_ERROR) from exc


# 서버가 도는 동안의 수명 주기(lifespan). stdio에서는 프로세스당 한 번 들어갔다 나온다.
# - 들어갈 때는 아무것도 하지 않는다. 모델은 첫 호출 때 올린다(시작할 때 올리면 클라이언트의 초기화 대기
#   시간을 넘길 수 있다).
# - 나갈 때 DB 엔진(app/db/session.py의 engine)을 한 번 닫는다. 클라이언트가 연결을 닫아 프로세스가 끝날 때
#   풀의 DB 연결을 닫고 끝내려는 것이다. 서비스와 평가·적재 스크립트는 이 엔진을 따로 닫지 않고 프로세스
#   종료에 맡기지만, 도구 서버는 클라이언트가 수시로 띄우고 닫는 자식 프로세스라 연결이 서버 쪽에 남지 않게
#   정리한다.
# 엔진은 닫은 뒤에도 다시 쓸 수 있다(풀을 새로 만든다).
@asynccontextmanager
async def _lifespan(server: MCPServer) -> AsyncIterator[None]:
    try:
        yield
    finally:
        await db_module.engine.dispose()


# MCP 서버를 만들어 도구 하나(search_fastapi_docs)를 등록해 돌려준다. 시험은 이 함수로 새 서버를 만든다.
# - 도구 주석: 읽기 전용(read_only_hint)·비파괴(destructive_hint False)·멱등(idempotent_hint, 같은 질문에
#   같은 결과)·닫힌 세계(open_world_hint False, 이 저장소의 문서 말고 바깥을 보지 않음). 클라이언트가 확인
#   절차를 고르는 데 쓰는 힌트다.
# - 도구 제목(title)은 사람이 보는 이름이고, 설명(description)은 모델에게 가는 TOOL_DESCRIPTION이다.
# - MCPServer를 만들 때 SDK가 루트 로거에 핸들러가 하나도 없으면 자기 핸들러(rich)를 달고 수준을 INFO로
#   바꾼다. 실제 실행에서는 main()이 앱의 configure_logging()을 먼저 불러 핸들러가 있으므로 아무것도 바뀌지
#   않는다. 하지만 시험이나 다른 프로그램이 build_server()만 부르면 그 프로세스의 로깅이 바뀌므로, 만들기
#   전의 핸들러 목록과 수준으로 되돌린다.
def build_server() -> MCPServer:
    root = logging.getLogger()
    handlers_before = list(root.handlers)
    level_before = root.level

    server = MCPServer(SERVER_NAME, instructions=SERVER_INSTRUCTIONS, lifespan=_lifespan)

    for handler in list(root.handlers):
        if handler not in handlers_before:
            root.removeHandler(handler)
            handler.close()
    if root.level != level_before:
        root.setLevel(level_before)

    server.add_tool(
        search_fastapi_docs,
        title="FastAPI 문서 검색",
        description=TOOL_DESCRIPTION,
        annotations=ToolAnnotations(
            read_only_hint=True,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        ),
    )
    return server


# 진입점: `python -m app.mcp_server`. 앱의 로깅(표준 오류, '시각 수준 이름 메시지' 형식)을 먼저 설정하고
# stdio 서버를 돌린다. 클라이언트가 표준 입력을 닫으면 lifespan을 정리하고 끝난다. 전송은 stdio뿐이다(위
# [설계 이유]).
def main() -> None:
    configure_logging()
    build_server().run("stdio")


if __name__ == "__main__":
    main()

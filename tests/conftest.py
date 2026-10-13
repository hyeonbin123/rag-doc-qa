"""Test fixtures.

Integration tests (test_auth.py, test_retrieval.py, test_query.py) need a
running Postgres+pgvector server reachable via TEST_DATABASE_URL (defaults to
the docker-compose db). The "ragdb_test" database and the extensions the
schema needs are created on first use.
"""

# [파일 역할] 모든 테스트가 공유하는 pytest 픽스처와 가짜 모델. 실제 Postgres + pgvector에 테스트용
# DB(ragdb_test)를 쓰고, 임베딩·생성 모델은 결정론적인 가짜로 바꿔 외부 API나 큰 모델 없이 돌게 한다(README
# '테스트').
# [왜 실제 DB인가] 벡터 검색(<=> 연산자), BM25 SQL, 생성 열 tsvector, 외래 키 연쇄 삭제처럼 DB가 하는 일이
# 많아서, 흉내 낸 DB로는 검증할 수 없다. CI도 pgvector 서비스 컨테이너를 띄워 같은 테스트를
# 돌린다(.github/workflows/ci.yml).
# [주요 구성] FakeEmbeddingService·FakeGenerationService(가짜 모델) → _ensure_test_database(DB·확장 자동 생성)
# → db_engine(테스트마다 스키마 생성·삭제) → db_session → client(의존성 교체한 HTTP 클라이언트) →
# authed_client(가입·로그인까지 마친 클라이언트).

import os

# pytest_asyncio: 비동기 픽스처. httpx의 ASGITransport: 서버를 띄우지 않고 FastAPI 앱을 메모리 안에서 바로
# 호출한다. SQLAlchemy: 테스트 DB 엔진·세션과 원시 SQL.
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

# 스키마 생성에 쓸 모델 메타데이터(Base), 바꿔 끼울 의존성(get_db, get_embedder, get_generator), 앱 본체,
# 가짜가 상속할 서비스 기반 클래스를 가져온다.
from app.db.base import Base
from app.db.session import get_db
from app.dependencies import get_embedder, get_generator
from app.main import app
from app.services.embedding import EmbeddingService
from app.services.generation import GenerationResult, GenerationService

# 기본값은 docker compose의 db(5432)에 있는 ragdb_test. 호스트 포트가 다르면(예: Windows가 5432를 예약해
# 55432로 띄운 경우) 환경 변수로 바꾼다(README '1. 환경 변수').
TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://raguser:ragpass@localhost:5432/ragdb_test",
)

# chunks.embedding 열이 vector(384)라서 가짜 벡터도 384차원으로 만든다.
EMBEDDING_DIM = 384


# 실제 sentence-transformers 모델 대신 쓰는 가짜 임베딩. 문자열의 바이트 합을 씨앗으로 384개 값을 만들어, 같은
# 텍스트는 항상 같은 벡터가 된다(결정론적). 모델 파일을 받거나 CPU 계산을 하지 않아 테스트가 빠르다.
# __init__을 건너뛰므로 revision·truncate_dim은 EmbeddingService의 클래스 기본값(None)을 쓰고, identity는
# 'fake-embedding'이 된다.
class FakeEmbeddingService(EmbeddingService):
    """Deterministic, dependency-free stand-in for the real sentence-transformer model."""

    def __init__(self) -> None:  # intentionally skip the real __init__/model load
        self.model_name = "fake-embedding"

    def _fake_vector(self, text: str) -> list[float]:
        seed = sum(text.encode("utf-8")) or 1
        return [((seed * (i + 1)) % 997) / 997 for i in range(EMBEDDING_DIM)]

    def embed_query(self, text: str) -> list[float]:
        return self._fake_vector(text)

    def embed_passages(self, texts: list[str]) -> list[list[float]]:
        return [self._fake_vector(t) for t in texts]


# LLM 대신 쓰는 가짜 생성기. 질문을 넣은 고정 답과, 받은 패시지를 모두 인용한 번호 목록을 바로 돌려준다.
# 라우터가 인용 번호를 청크로 바꾸는 흐름을 GPU 없이 검증할 수 있다.
class FakeGenerationService(GenerationService):
    async def answer(self, question, chunks, language="en"):
        cited = list(range(1, len(chunks) + 1))
        return GenerationResult(
            answer=f"Fake answer for: {question}",
            cited_chunk_numbers=cited,
            input_tokens=10,
            output_tokens=10,
            model_name="fake-model",
        )


# 테스트 DB 준비를 프로세스당 한 번만 하려는 플래그.
_test_database_ready = False


# ragdb_test가 없으면 만들고, 스키마에 필요한 확장(vector: pgvector, pgcrypto: UUID 생성 함수)을 켠다.
# CREATE DATABASE는 트랜잭션 안에서 실행할 수 없어서, 관리용 postgres DB에 AUTOCOMMIT 연결로 접속해 만든다. DB
# 이름은 SQL 파라미터로 넘길 수 없어 큰따옴표로 감싸 문자열에 넣는다(값은 코드의 URL에서 온다).
async def _ensure_test_database() -> None:
    """Create the test database and its extensions if missing.

    docker compose only creates the app database, so without this a fresh clone
    fails every integration test on "database ragdb_test does not exist".
    """
    global _test_database_ready
    if _test_database_ready:
        return

    url = make_url(TEST_DATABASE_URL)
    admin = create_async_engine(url.set(database="postgres"), isolation_level="AUTOCOMMIT")
    async with admin.connect() as conn:
        exists = await conn.scalar(
            text("SELECT 1 FROM pg_database WHERE datname = :name"), {"name": url.database}
        )
        if not exists:
            await conn.execute(text(f'CREATE DATABASE "{url.database}"'))
    await admin.dispose()

    engine = create_async_engine(url)
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pgcrypto"))
    await engine.dispose()
    _test_database_ready = True


# 테스트마다 모델 메타데이터로 모든 테이블을 만들고(create_all), 끝나면 모두 지운다(drop_all). 테스트끼리
# 데이터가 섞이지 않는다. alembic 마이그레이션이 아니라 모델 정의로 만든 스키마다.
@pytest_asyncio.fixture
async def db_engine():
    await _ensure_test_database()
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


# 테스트 하나가 쓰는 DB 세션. expire_on_commit=False로 커밋 뒤에도 객체 속성을 다시 조회하지 않고 읽을 수 있게
# 한다.
@pytest_asyncio.fixture
async def db_session(db_engine):
    session_maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with session_maker() as session:
        yield session


# 앱의 의존성을 테스트용으로 바꾼 HTTP 클라이언트. DB는 위 테스트 세션, 임베딩은 언어와 상관없이 가짜 임베딩을
# 돌려주는 조회 함수, 생성은 가짜 생성기로 바꾼다. 테스트가 끝나면 교체를 모두 되돌려 다음 테스트에 남지 않게
# 한다.
@pytest_asyncio.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_embedder] = lambda: lambda language="en": FakeEmbeddingService()
    app.dependency_overrides[get_generator] = lambda: FakeGenerationService()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


# 가입과 로그인을 실제 API로 마치고 Authorization: Bearer 헤더를 붙인 클라이언트. 인증이 필요한 엔드포인트
# 테스트가 쓴다.
@pytest_asyncio.fixture
async def authed_client(client, db_session):
    resp = await client.post(
        "/auth/register", json={"email": "test@example.com", "password": "testpass123"}
    )
    assert resp.status_code == 201

    login_resp = await client.post(
        "/auth/login",
        data={"username": "test@example.com", "password": "testpass123"},
    )
    token = login_resp.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    yield client

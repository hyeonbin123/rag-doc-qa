# [파일 역할] 앱 전체가 공유하는 비동기 DB 엔진(커넥션 풀)과 세션 팩토리를 만든다.
# [연결] 라우터는 FastAPI 의존성 get_db로 요청마다 세션을 받는다. 수집·시드
# 스크립트(scripts/ingest_fastapi_docs.py, scripts/seed_demo_user.py)와 평가
# 스크립트(eval/run_retrieval_eval.py, eval/run_answer_eval.py)는 async_session_maker를 직접 쓴다. 테스트는
# get_db를 테스트 DB 세션으로 바꿔 끼운다(tests/conftest.py).

from collections.abc import AsyncGenerator

# SQLAlchemy 2.0 비동기 API. FastAPI 핸들러가 async라 DB 대기 중에도 이벤트 루프가 다른 요청을 처리할 수 있게
# asyncpg 드라이버와 함께 쓴다.
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import get_settings

# 모듈을 처음 import할 때 설정을 읽고 엔진을 하나 만든다(프로세스당 커넥션 풀 하나).
settings = get_settings()

# pool_pre_ping=True: 풀에서 연결을 꺼낼 때 살아 있는지 먼저 확인한다. DB 컨테이너가 재시작돼 끊긴 연결을 받아
# 첫 요청이 실패하는 일을 막는다.
# expire_on_commit=False: 커밋한 뒤에도 객체 속성을 그대로 읽을 수 있게 한다. 비동기 세션에서는 만료된 속성을
# 다시 읽으려면 DB 왕복이 필요해 지연 로딩 오류가 나기 쉽다. /query/ask가 중간에 commit한 뒤에도
# current_user를 쓰는 것이 이 설정 덕분이다(app/routers/query.py 주석).
engine = create_async_engine(settings.database_url, pool_pre_ping=True)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


# FastAPI 의존성: 요청마다 새 세션을 열어 넘기고, 응답이 끝나면 async with가 세션을 닫아 연결을 풀에 돌려준다.
# 커밋은 각 핸들러가 직접 한다.
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

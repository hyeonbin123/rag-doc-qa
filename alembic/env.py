# [파일 역할] Alembic이 마이그레이션(alembic/versions/*)을 실행할 때 가장 먼저 읽는 진입 스크립트다. 어느 DB에
# 붙을지, 어떤 메타데이터를 기준으로 삼을지 정하고 마이그레이션을 실제로 돌린다.
# [왜 필요한가] 앱은 비동기 드라이버(DATABASE_URL이 postgresql+asyncpg://...)로 DB에 붙는데, Alembic의
# 마이그레이션 API는 동기 방식이다. 그래서 비동기 엔진으로 연결한 뒤 run_sync로 동기 함수를 그 연결 위에서
# 실행하는 다리 역할을 이 파일이 맡는다.
# [흐름] 설정 읽기(alembic.ini 로깅 + 앱 Settings의 DB 주소) → 오프라인 모드면 SQL 문만 만들고, 아니면 비동기
# 엔진으로 접속해 마이그레이션을 실행한다.
# [연결] Dockerfile CMD와 docker-compose.yml의 command가 서버를 띄우기 전에 `alembic upgrade head`로 이 파일을
# 거친다. 테스트(tests/conftest.py)는 Alembic을 쓰지 않고 Base.metadata.create_all로 스키마를 만든다.

import asyncio
from logging.config import fileConfig

# create_async_engine: 앱과 같은 asyncpg 주소를 그대로 쓰려면 비동기 엔진이 필요하다. 동기 엔진으로는
# postgresql+asyncpg 주소에 붙을 수 없다.
from sqlalchemy.ext.asyncio import create_async_engine

# context: Alembic이 실행 중에 넘겨 주는 설정·실행 환경 객체.
# app.config / app.db.base: DB 주소와 선언형 Base를 앱과 같은 곳에서 가져와, 마이그레이션과 앱이 서로 다른
# DB를 보지 않게 한다.
# app.models 묶음 import: 모델 클래스가 정의되는 순간 Base.metadata에 테이블이 등록되므로, 이름을 쓰지
# 않더라도 불러와 두어야 target_metadata에 모든 테이블이 들어간다(그래서 사용하지 않는 import 경고를 끄는 기존
# 주석이 붙어 있다).
from alembic import context
from app.config import get_settings
from app.db.base import Base
from app.models import chunk, document, query_log, user  # noqa: F401  (모델을 메타데이터에 등록)

# alembic.ini 내용을 담은 설정 객체. 아래에서 DB 주소를 이 객체에 덮어쓴다.
config = context.config

# alembic.ini의 [loggers] 설정으로 파이썬 로깅을 맞춘다. 설정 파일 없이 코드에서 호출된 경우에는 건너뛴다.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Alembic이 '모델이 기대하는 스키마'로 삼는 메타데이터. 자동 생성(autogenerate)이 DB와 모델을 비교할 때 이것을
# 본다. 이 저장소의 마이그레이션 파일은 op.create_table 등으로 직접 작성돼 있다.
target_metadata = Base.metadata

# DB 주소를 alembic.ini에 적지 않고 앱 설정(.env 또는 환경 변수 DATABASE_URL)에서 가져온다. 주소를 한곳에서만
# 관리하므로, compose가 컨테이너 안에서 DATABASE_URL을 db 서비스 주소로 덮어쓰면 마이그레이션도 자동으로 같은
# DB를 향한다.
settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.database_url)


# 오프라인 모드(`alembic upgrade head --sql`): DB에 접속하지 않고 실행될 SQL 문만 출력한다. DBA에게 SQL을
# 넘기거나 변경 내용을 미리 볼 때 쓰는 Alembic 표준 경로다.
# literal_binds=True는 바인드 파라미터 자리에 실제 값을 글자 그대로 넣어, 출력된 SQL을 그대로 실행할 수 있게
# 한다.
def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


# 이미 열린 연결 위에서 마이그레이션을 실행하는 동기 함수. 아래 run_migrations_online이 connection.run_sync로
# 이 함수를 부른다. 한 트랜잭션 안에서 돌기 때문에 PostgreSQL에서는 중간에 실패하면 DDL까지 함께 되돌려진다.
def do_run_migrations(connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


# 온라인 모드(기본): 실제 DB에 비동기 엔진으로 접속해 마이그레이션을 실행한다.
# run_sync는 비동기 연결을 동기 연결처럼 감싸 동기 함수에 넘겨 준다. Alembic의 동기 API를 바꾸지 않고 asyncpg
# 드라이버를 쓸 수 있는 SQLAlchemy 공식 방식이다.
# 끝나면 dispose로 커넥션 풀을 닫아, 짧게 실행되는 마이그레이션 프로세스가 연결을 남기지 않게 한다.
async def run_migrations_online() -> None:
    connectable = create_async_engine(config.get_main_option("sqlalchemy.url"))

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


# Alembic이 이 스크립트를 불러오면 곧바로 모드에 맞는 경로를 실행한다. 온라인 경로는 코루틴이라
# asyncio.run으로 이벤트 루프를 만들어 돌린다.
if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())

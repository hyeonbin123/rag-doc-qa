# [테스트 묶음] 질문 기록 API(/logs, app/routers/logs.py)와 query_logs 인덱스 테스트.
# - 입력 검증: 잘못된 id와 범위를 벗어난 페이지 값이 500이 아니라 422로 끝나는지.
# - 상세 목록(detail=true): 목록 항목이 단건 상세(/logs/{id})와 같은 필드를 담고, 본인 기록만 최신순으로
#   limit·offset대로 오는지. 기본 목록(detail 없음·false)은 detail 인자가 생기기 전과 바이트 단위로 같은지.
# - 인덱스: 모델(app/models/query_log.py)과 마이그레이션 0005가 같은 (user_id, created_at DESC) 인덱스를
#   만들고, '내 최근 기록' 질의가 정렬 단계 없이 그 인덱스로 읽히는지.
# [왜 중요한가] 기록 id를 UUID로, limit을 1~100, offset을 0 이상으로 검증하기 전에는 이런 입력이 Postgres까지
# 가서 500이 났다(커밋 9e7d6eb). 목록이 요약만 주던 때는 채팅 화면이 로그인마다 목록 1번과 항목별 상세 10번,
# 모두 11번을 요청했고, 인덱스가 없을 때는 이 질의가 query_logs 전체를 훑은 뒤 정렬했다.
# [import] importlib.util·io·Path·MigrationContext·Operations·ScriptDirectory·Config는 마이그레이션 파일을
# DB 없이 SQL 문자열로 그려 보고 리비전 사슬을 읽는 데, CreateIndex·postgresql은 모델의 인덱스를 같은 방언의
# DDL로 바꾸는 데 쓴다.

import importlib.util
import io
import uuid
from datetime import UTC, datetime
from pathlib import Path

import pytest
from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.operations import Operations
from alembic.script import ScriptDirectory
from sqlalchemy import text
from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateIndex

from app.models.query_log import QueryLog
from app.models.user import User
from app.schemas.logs import QueryLogDetail

# ROOT: 저장소 루트(alembic/ 폴더가 있는 곳). 테스트를 어느 폴더에서 돌려도 같은 마이그레이션 파일을 읽는다.
# INDEX_NAME: 모델과 마이그레이션 0005가 함께 쓰는 인덱스 이름.
ROOT = Path(__file__).resolve().parents[1]
INDEX_NAME = "ix_query_logs_user_id_created_at"


# UUID가 아닌 기록 id는 422.
@pytest.mark.asyncio
async def test_a_malformed_log_id_is_rejected_not_a_server_error(authed_client):
    resp = await authed_client.get("/logs/not-a-uuid")
    assert resp.status_code == 422


# 형식은 맞지만 없는(또는 다른 사용자의) 기록 id는 404.
@pytest.mark.asyncio
async def test_an_unknown_log_id_is_not_found(authed_client):
    resp = await authed_client.get(f"/logs/{uuid.uuid4()}")
    assert resp.status_code == 404


# limit 음수·0·101, offset 음수는 모두 422. 경계 밖 값 네 가지를 parametrize로 한 번에 검사한다.
@pytest.mark.asyncio
@pytest.mark.parametrize("query", ["limit=-1", "offset=-1", "limit=0", "limit=101"])
async def test_paging_outside_the_bounds_is_rejected(authed_client, query):
    # 예전에는 음수 값이 Postgres까지 가서 거부되며 500이 났다.
    resp = await authed_client.get(f"/logs?{query}")
    assert resp.status_code == 422


# 경계 안의 최댓값(limit=100, offset=0)은 200이고, 질문한 적이 없는 새 사용자라 빈 목록이다.
@pytest.mark.asyncio
async def test_paging_within_the_bounds_works(authed_client):
    resp = await authed_client.get("/logs?limit=100&offset=0")
    assert resp.status_code == 200
    assert resp.json() == []


# 질문 기록 한 행을 만든다. created_at을 직접 정해 순서를 확실히 한다(한 트랜잭션 안의 now()는 모두 같은
# 시각이라 server_default에 맡기면 순서가 정해지지 않는다). 상세 필드도 /query/ask가 저장하는 모양
# (app/routers/query.py)대로 모두 채워 목록과 단건 상세를 비교할 수 있게 한다. overrides로 필드를 바꾼다.
def _log(user_id: uuid.UUID, minute: int, question: str, **overrides) -> QueryLog:
    values = {
        "user_id": user_id,
        "question": question,
        "answer": f"answer to {question}",
        "retrieved_chunks": [
            {
                "chunk_id": str(uuid.uuid4()),
                "document_id": str(uuid.uuid4()),
                "source_path": "docs/en/docs/tutorial/body.md",
                "score": 0.75,
                "cited": True,
            },
            {
                "chunk_id": str(uuid.uuid4()),
                "document_id": str(uuid.uuid4()),
                "source_path": "docs/en/docs/tutorial/query-params.md",
                "score": 0.5,
                "cited": False,
            },
        ],
        "model_name": "fake-model",
        "prompt_tokens": 11,
        "completion_tokens": 7,
        "embedding_latency_ms": 3,
        "retrieval_latency_ms": 5,
        "generation_latency_ms": 40,
        "total_latency_ms": 48,
        "created_at": datetime(2026, 10, 1, 9, minute, tzinfo=UTC),
    }
    values.update(overrides)
    return QueryLog(**values)


# 로그인한 테스트 사용자(authed_client가 가입한 계정)의 id를 /auth/me로 읽는다.
async def _my_id(authed_client) -> uuid.UUID:
    return uuid.UUID((await authed_client.get("/auth/me")).json()["id"])


# 행을 저장한 뒤 세션의 객체를 모두 떼어 낸다(expunge_all). 테스트와 앱이 같은 세션을 쓰므로, 떼어 내지 않으면
# 앱의 SELECT가 DB에서 읽은 값 대신 테스트가 만든 파이썬 객체를 그대로 돌려줘 실제 요청과 달라진다.
async def _save(db_session, *rows) -> None:
    db_session.add_all(rows)
    await db_session.commit()
    db_session.expunge_all()


# detail=true면 목록 항목마다 단건 상세(/logs/{id})와 같은 필드·값이 온다. 다른 사용자의 기록은 섞이지
# 않고, 최신순이며 limit·offset이 그대로 적용된다. 채팅 화면은 이 응답 하나로 인용(cited인
# retrieved_chunks)과 단계별 지연을 그린다(app/web/static/chat.js의 loadHistory).
@pytest.mark.asyncio
async def test_detail_lists_only_my_logs_newest_first_with_the_detail_fields(authed_client, db_session):
    me = await _my_id(authed_client)
    other = User(email="other@example.com", hashed_password="not-a-real-hash")
    db_session.add(other)
    await db_session.flush()
    await _save(
        db_session,
        _log(me, 1, "oldest"),
        _log(other.id, 2, "someone else's"),
        _log(me, 3, "middle"),
        _log(me, 4, "newest", model_name=None, total_latency_ms=None),
    )

    resp = await authed_client.get("/logs?detail=true&limit=2")

    assert resp.status_code == 200
    items = resp.json()
    assert [item["question"] for item in items] == ["newest", "middle"]
    assert list(items[0]) == list(QueryLogDetail.model_fields)
    assert items[1]["retrieved_chunks"][0]["cited"] is True
    assert items[1]["generation_latency_ms"] == 40
    assert items[0]["model_name"] is None and items[0]["total_latency_ms"] is None
    for item in items:
        assert item == (await authed_client.get(f"/logs/{item['id']}")).json()

    # 다음 쪽에는 내 가장 오래된 기록 하나만 남는다(다른 사용자의 기록은 어느 쪽에도 나오지 않는다).
    rest = (await authed_client.get("/logs?detail=true&limit=2&offset=2")).json()
    assert [item["question"] for item in rest] == ["oldest"]


# 기본 목록(detail 없음)과 detail=false는 detail 인자가 생기기 전 응답과 바이트 단위로 같다: 요약 다섯
# 필드가 같은 순서로, 같은 JSON 표기(공백 없음, 한글·이모지는 그대로, 따옴표·줄바꿈·탭만 이스케이프, 시각은
# UTC 'Z')로 온다. 기대 바이트는 detail 인자를 더하기 전 코드에서 이 테스트가 통과해 그때의 실제 응답과 같음을
# 확인했다. 이 목록을 읽는 다른 클라이언트가 깨지지 않게 고정한다.
@pytest.mark.asyncio
async def test_the_default_list_keeps_its_summary_bytes(authed_client, db_session):
    me = await _my_id(authed_client)
    await _save(
        db_session,
        _log(
            me,
            0,
            '한국어 "질문"\n\t<b>',
            id=uuid.UUID("00000000-0000-4000-8000-000000000001"),
            answer="답 `코드` 😀",
            total_latency_ms=None,
            created_at=datetime(2026, 10, 1, 9, 0, 0, 123456, tzinfo=UTC),
        ),
        _log(me, 5, "newer", id=uuid.UUID("00000000-0000-4000-8000-000000000002")),
    )
    expected = (
        '[{"id":"00000000-0000-4000-8000-000000000002","question":"newer",'
        '"answer":"answer to newer","total_latency_ms":48,"created_at":"2026-10-01T09:05:00Z"},'
        '{"id":"00000000-0000-4000-8000-000000000001","question":"한국어 \\"질문\\"\\n\\t<b>",'
        '"answer":"답 `코드` 😀","total_latency_ms":null,"created_at":"2026-10-01T09:00:00.123456Z"}]'
    ).encode()

    for path in ("/logs", "/logs?detail=false"):
        resp = await authed_client.get(path)
        assert resp.status_code == 200, path
        assert resp.headers["content-type"] == "application/json", path
        assert resp.content == expected, path


# detail은 참·거짓 값만 받는다. 알아볼 수 없는 값은 조용히 요약으로 넘기지 않고 422로 알린다.
@pytest.mark.asyncio
async def test_a_detail_value_that_is_not_a_boolean_is_rejected(authed_client):
    resp = await authed_client.get("/logs?detail=maybe")
    assert resp.status_code == 422


# 상세 목록도 로그인이 필요하다(토큰 없으면 401).
@pytest.mark.asyncio
async def test_the_detail_list_needs_a_login(client):
    resp = await client.get("/logs?detail=true")
    assert resp.status_code == 401


# 모델이 (user_id, created_at DESC) 인덱스를 선언한다. 테스트 DB는 모델로 만들므로(create_all) 이
# 선언이 테스트 스키마의 인덱스가 되고, PostgreSQL 방언 DDL로 바꾼 문장이 마이그레이션 0005와 같아야
# 한다(아래 테스트).
def test_the_model_declares_the_user_newest_first_index():
    index = {i.name: i for i in QueryLog.__table__.indexes}[INDEX_NAME]
    ddl = str(CreateIndex(index).compile(dialect=postgresql.dialect()))

    assert ddl == f"CREATE INDEX {INDEX_NAME} ON query_logs (user_id, created_at DESC)"


# 마이그레이션 파일 하나를 모듈로 불러 upgrade나 downgrade를 DB 없이 SQL 문자열로 그린다(alembic의
# as_sql 오프라인 모드). 파일 이름이 숫자로 시작해 일반 import로는 불러올 수 없어 파일 경로로 불러온다.
# 돌려주는 SQL은 공백·줄바꿈을 한 칸으로 줄인 문자열이다.
def _render_migration(filename: str, step: str) -> str:
    spec = importlib.util.spec_from_file_location(
        "migration_under_test", ROOT / "alembic" / "versions" / filename
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    buffer = io.StringIO()
    context = MigrationContext.configure(
        dialect_name="postgresql", opts={"as_sql": True, "output_buffer": buffer}
    )
    with Operations.context(context):
        getattr(module, step)()
    return " ".join(buffer.getvalue().split())


# 마이그레이션 0005가 0004 다음의 유일한 head이고, 모델과 같은 DDL로 인덱스를 만들며 downgrade는 그
# 인덱스만 지운다. 둘이 어긋나면 테스트 스키마(모델)와 실제 DB 스키마(마이그레이션)가 달라진다.
def test_migration_0005_creates_the_same_index_as_the_model():
    # alembic.ini를 읽지 않고 버전 폴더 위치만 준다(리비전 사슬을 읽는 데는 이것만 필요하다). ini를 읽으면
    # path_separator가 없는 prepend_sys_path 때문에 alembic 1.19가 DeprecationWarning을 낸다.
    config = Config()
    config.set_main_option("script_location", str(ROOT / "alembic"))
    script = ScriptDirectory.from_config(config)
    assert script.get_heads() == ["0005"]
    assert script.get_revision("0005").down_revision == "0004"

    index = {i.name: i for i in QueryLog.__table__.indexes}[INDEX_NAME]
    model_ddl = str(CreateIndex(index).compile(dialect=postgresql.dialect()))
    filename = "0005_query_logs_user_created_at.py"

    assert _render_migration(filename, "upgrade") == model_ddl + ";"
    assert _render_migration(filename, "downgrade") == f"DROP INDEX {INDEX_NAME};"


# 테스트 DB(create_all)에 인덱스가 실제로 (user_id, created_at DESC)로 만들어지고, 목록 질의(한 사용자,
# 최신순, LIMIT)가 정렬 단계 없이 그 인덱스로 읽힌다. 행이 몇 개뿐인 테스트 DB에서는 플래너가 순차 탐색을
# 고를 수 있어, 이 트랜잭션에서만(SET LOCAL) 순차·비트맵 탐색과 정렬을 꺼 '인덱스로 순서대로 읽을 수
# 있는가'만 본다. 인덱스가 없으면 꺼 둔 정렬을 쓸 수밖에 없어 계획에 Sort가 남는다.
@pytest.mark.asyncio
async def test_my_newest_logs_are_read_through_the_index_without_a_sort(db_session):
    indexdef = await db_session.scalar(
        text("SELECT indexdef FROM pg_indexes WHERE indexname = :name"), {"name": INDEX_NAME}
    )
    assert indexdef == (
        f"CREATE INDEX {INDEX_NAME} ON public.query_logs USING btree (user_id, created_at DESC)"
    )

    for setting in ("enable_seqscan", "enable_bitmapscan", "enable_sort"):
        await db_session.execute(text(f"SET LOCAL {setting} = off"))
    user_id = uuid.uuid4()  # 테스트가 만든 UUID라 SQL 문자열에 넣어도 안전하다
    plan = "\n".join(
        await db_session.scalars(
            text(
                "EXPLAIN SELECT * FROM query_logs "
                f"WHERE user_id = '{user_id}' ORDER BY created_at DESC LIMIT 20"
            )
        )
    )

    assert f"Index Scan using {INDEX_NAME}" in plan, plan
    assert "Sort" not in plan, plan

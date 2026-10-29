"""query_logs에 '내 최근 기록' 인덱스 (user_id, created_at DESC)를 더한다.

GET /logs는 로그인한 사용자 한 명의 기록을 최신순으로 몇 개만 읽는데, 0001은 query_logs에 기본 키 말고는
인덱스를 만들지 않아 이 질의가 테이블 전체를 훑은 뒤 정렬했다.

Revision ID: 0005
Revises: 0004
Create Date: 2026-10-30

"""
# [파일 역할] query_logs에 ix_query_logs_user_id_created_at = (user_id, created_at DESC) 인덱스를 만든다.
# [왜 필요한가] GET /logs(app/routers/logs.py)의 질의 WHERE user_id = 나 ORDER BY created_at DESC LIMIT n이 이
# 인덱스를 앞에서부터 n개만 읽으면 되어, 정렬 단계 없이 끝난다. 채팅 화면이 로그인할 때마다 이 질의를 부르고,
# 질문마다 한 행씩 늘어난다. 앞 열이 user_id라, 사용자를 지울 때 DB가 그 사용자의 기록을 찾아 user_id를 NULL로
# 바꾸는 일(0001의 ON DELETE SET NULL)도 이 인덱스로 찾을 수 있다. PostgreSQL은 외래 키 열에 인덱스를 저절로
# 만들지 않는다.
# [모델과 함께] app/models/query_log.py가 같은 이름·정의의 Index를 선언한다. 테스트(tests/test_logs.py)가 이
# 파일의 SQL과 모델의 DDL이 같은지 확인한다.
# [주의] CONCURRENTLY 없이 만든다. alembic은 마이그레이션을 트랜잭션 안에서 돌리는데 CREATE INDEX
# CONCURRENTLY는 트랜잭션 안에서 쓸 수 없고, 이 앱은 서버(uvicorn)를 띄우기 전에 마이그레이션을 적용하므로
# (docker-compose.yml, Dockerfile의 alembic upgrade head) 인덱스를 만드는 동안 기록을 쓰는 요청이 없다.
# 인덱스를 만드는 동안 query_logs 쓰기는 잠기고 읽기는 된다.

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# 리비전 사슬: 0004 다음.
revision: str = "0005"
down_revision: str | None = "0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# 모델(app/models/query_log.py)의 Index와 같은 이름. 마이그레이션은 그 시점의 스키마를 고정해야 하므로
# 모델에서 가져오지 않고 직접 적는다.
INDEX_NAME = "ix_query_logs_user_id_created_at"


def upgrade() -> None:
    # created_at DESC는 열 이름이 아니라 정렬 방향이 붙은 식이라 text로 넘긴다. 결과 SQL:
    # CREATE INDEX ix_query_logs_user_id_created_at ON query_logs (user_id, created_at DESC)
    op.create_index(INDEX_NAME, "query_logs", ["user_id", sa.text("created_at DESC")])


def downgrade() -> None:
    # 되돌리기: 이 인덱스만 지운다. 테이블과 행은 그대로다.
    op.drop_index(INDEX_NAME, table_name="query_logs")

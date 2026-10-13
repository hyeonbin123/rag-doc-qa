"""add language to chunks

Revision ID: 0003
Revises: 0002
Create Date: 2026-09-12

"""
# [파일 역할] chunks에 language 열("en" / "ko")을 더한다. 한국어 번역 문서(docs/ko/docs/)를 함께 적재하면서
# 생겼다(docs/experiments.md v8).
# [왜 필요한가] 영어와 한국어 청크는 서로 다른 임베딩 모델로 만든 벡터라 같은 공간에서 비교하면 안 된다.
# 검색은 항상 질문 언어 한 가지 안에서만 하므로, 각 청크가 어느 언어인지 저장해 두고 WHERE language = ... 로
# 거른다. 문서 테이블과 조인하지 않고 거를 수 있게 청크 쪽에 둔다(app/models/chunk.py 주석).
# [이어지는 변경] 0004가 이 열을 조건으로 언어별 부분 HNSW 인덱스를 만든다.

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# 리비전 사슬: 0002 다음.
revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Every existing row is English: until now only docs/en/docs was ingested.
    # server_default="en": 기존 행을 모두 영어로 채우면서 NOT NULL 열을 한 번에 추가한다(기본값 없이 NOT NULL
    # 열을 더하면 기존 행 때문에 실패한다). String(8)은 'en', 'ko' 같은 짧은 언어 코드용이다.
    op.add_column(
        "chunks",
        sa.Column("language", sa.String(8), nullable=False, server_default="en"),
    )


def downgrade() -> None:
    op.drop_column("chunks", "language")

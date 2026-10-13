"""add full-text search column to chunks

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-11

"""
# [파일 역할] chunks에 전문 검색용 tsvector 열(content_tsv)과 GIN 인덱스를 더한다. hybrid·rerank 검색 모드의
# 키워드(어휘) 검색이 이 열을 쓴다.
# [설계 이유] 일반 열이 아니라 생성 열(GENERATED ... STORED)로 만들어 PostgreSQL이 heading_path·content가 바뀔
# 때마다 알아서 다시 계산하게 한다. README '설계 판단'에 적힌 대로 수집 코드가 이 열을 따로 신경 쓸 필요가
# 없다.
# [배경] docs/experiments.md v4(ts_rank + RRF)에서 처음 추가했고, v5부터는 같은 열의 위치 정보로 BM25를
# SQL에서 계산한다(app/services/retrieval.py).

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import TSVECTOR

from alembic import op

# 리비전 사슬: 0001 다음.
revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # content_tsv = to_tsvector('english', 헤딩 경로 + ' ' + 본문).
    # - 'english' 설정: 영어 형태소 정규화(어간 추출, 불용어 제거)를 한다. 그래서 한국어 청크에서는 영어
    #   단어(API 이름 등)만 쓸모 있는 어휘가 된다(README '알려진 한계'의 한국어 hybrid 미측정 이유).
    # - coalesce: heading_path가 NULL이면 문자열 연결 전체가 NULL이 되므로 빈 문자열로 바꾼다.
    # - 헤딩을 본문 앞에 붙여, 본문에 절 제목 단어가 없어도 제목으로 검색되게 한다.
    # - persisted=True: 저장되는 생성 열(STORED). 검색할 때마다 다시 계산하지 않는다.
    op.add_column(
        "chunks",
        sa.Column(
            "content_tsv",
            TSVECTOR,
            sa.Computed(
                "to_tsvector('english', coalesce(heading_path, '') || ' ' || content)",
                persisted=True,
            ),
        ),
    )
    # GIN 역색인: 어휘소 → 그 어휘소가 든 청크 목록. `@@` 검색과, BM25에서 질문 어휘소별 문서 빈도(df)를 세는
    # 질의를 빠르게 한다. 모델(app/models/chunk.py)의 Index 선언과 이름이 같아 테스트의 create_all로 만든
    # 스키마와도 일치한다.
    op.create_index("ix_chunks_content_tsv", "chunks", ["content_tsv"], postgresql_using="gin")


def downgrade() -> None:
    op.drop_index("ix_chunks_content_tsv", table_name="chunks")
    op.drop_column("chunks", "content_tsv")

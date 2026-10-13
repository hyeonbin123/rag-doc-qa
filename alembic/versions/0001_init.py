"""init schema: extensions, users, documents, chunks, query_logs

Revision ID: 0001
Revises:
Create Date: 2026-09-11

"""
# [파일 역할] 첫 번째 마이그레이션. 빈 DB에 서비스의 기본 스키마(확장 2개, users / documents / chunks /
# query_logs 테이블, 벡터 인덱스)를 만든다.
# [설계 이유] 별도 벡터 DB를 두지 않고 PostgreSQL + pgvector 하나에 관계형 데이터와 임베딩 벡터를 함께 둔다.
# README '설계 판단'에 따르면 이 규모에서는 한 DB로 다루는 쪽이 운영 부담이 적다.
# [테이블 관계] documents 1 : N chunks(문서를 잘게 나눈 검색 단위, 벡터 포함), users 1 : N query_logs(질문
# 하나당 한 행, 검색 결과와 단계별 지연 기록).
# [이후 변경] 0002에서 전문 검색 열(content_tsv), 0003에서 언어 열(language), 0004에서 언어별 HNSW 인덱스로
# 바뀐다. 스키마를 바꿀 때는 앱 모델(app/models/*)도 함께 고쳐야 한다.

from collections.abc import Sequence

# sqlalchemy: 열 타입·제약을 선언한다. pgvector.sqlalchemy.Vector: pgvector의 vector(n) 열 타입. JSONB·UUID:
# PostgreSQL 전용 타입(검색 결과 목록 저장, 기본 키).
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import JSONB, UUID

from alembic import op

# Alembic 리비전 사슬: 이 파일의 ID는 0001이고, 앞선 리비전이 없으므로(down_revision=None) 사슬의 시작이다.
revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# 임베딩 벡터 차원. 처음 쓴 영어 모델 BAAI/bge-small-en-v1.5의 출력 크기다. 이후 한국어 모델도 이 열에 맞춰
# 384차원을 쓴다(e5-small은 원래 384, Granite R2 311M은 384로 잘라 씀).
# 앱 모델(app/models/chunk.py)의 같은 이름 상수와 값이 같아야 한다. 마이그레이션 안에 값을 직접 적어 두면
# 나중에 앱 코드가 바뀌어도 이미 적용된 이 마이그레이션의 내용은 바뀌지 않는다.
EMBEDDING_DIM = 384


def upgrade() -> None:
    # vector: pgvector 확장(벡터 열 타입과 거리 연산자, HNSW 인덱스). pgcrypto: UUID 기본값에 쓰는
    # gen_random_uuid()를 제공하던 확장이다(PostgreSQL 13부터는 이 함수가 기본 내장). IF NOT EXISTS로 이미
    # 설치된 DB에서도 실패하지 않게 한다. 테스트용 DB에서도 tests/conftest.py가 같은 두 확장을 만든다.
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    # users: 로그인 계정. id는 DB가 gen_random_uuid()로 만드는 무작위 UUID다. hashed_password에는 bcrypt 해시
    # 문자열이 들어간다(원문 비밀번호는 저장하지 않는다). created_at은 시간대 포함 타입으로 저장한다.
    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    # 모델(app/models/user.py)의 index=True에 해당하는 이름 있는 인덱스. 이 마이그레이션에서는 unique=True가
    # 만드는 유일 제약 인덱스와 같은 열에 인덱스가 하나 더 생긴다.
    op.create_index("ix_users_email", "users", ["email"])

    # documents: 수집한 마크다운 문서 한 개당 한 행. source_path(저장소 안 경로, 예: docs/en/docs/...)가
    # 문서의 고유 식별자다. source_commit_sha는 어느 커밋에서 가져왔는지(git SHA-1 16진수 40자),
    # content_hash는 재수집 때 바뀐 문서만 다시 처리하려고 저장하는 SHA-256
    # 16진수(64자)다(app/services/ingestion.py).
    op.create_table(
        "documents",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("source_path", sa.String(512), nullable=False, unique=True),
        sa.Column("title", sa.String(255), nullable=True),
        sa.Column("source_commit_sha", sa.String(40), nullable=False),
        sa.Column("content_hash", sa.String(64), nullable=False),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_documents_source_path", "documents", ["source_path"])

    # chunks: 검색 단위. 문서를 청킹한 조각마다 본문, 헤딩 경로(인용에 표시), 토큰 수, 임베딩 벡터를 저장한다.
    # - ondelete="CASCADE": 문서 행을 지우면 그 청크도 DB가 함께 지운다(재수집에서 사라진 문서를 정리할 때
    #   청크를 따로 지울 필요가 없다).
    # - token_count: BM25 점수의 문서 길이 정규화에 쓴다(app/services/retrieval.py).
    # - (document_id, chunk_index) 유일 제약: 한 문서 안에서 청크 순번이 겹치지 않게 한다.
    op.create_table(
        "chunks",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "document_id",
            UUID(as_uuid=True),
            sa.ForeignKey("documents.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("chunk_index", sa.Integer, nullable=False),
        sa.Column("heading_path", sa.String(512), nullable=True),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("token_count", sa.Integer, nullable=False),
        sa.Column("embedding", Vector(EMBEDDING_DIM), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("document_id", "chunk_index"),
    )
    # 임베딩 열의 HNSW 근사 최근접 이웃 인덱스. vector_cosine_ops는 코사인 거리(<=> 연산자)로 탐색하게 한다.
    # m=16, ef_construction=64는 pgvector 기본값과 같은 그래프 연결 수·구축 탐색 폭이다. README '설계 판단'에
    # 따르면 HNSW는 IVFFlat과 달리 list 수 튜닝이 필요 없어서 골랐다. 0004에서 언어별 부분 인덱스 두 개로
    # 바뀐다.
    op.execute(
        "CREATE INDEX chunks_embedding_hnsw_idx ON chunks "
        "USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64)"
    )

    # query_logs: /query/ask 호출 한 번의 기록. 질문, 답변, 검색된 청크 목록(JSONB: 청크 id·문서
    # id·경로·점수·인용 여부), 모델 이름, 토큰 수, 단계별 지연(임베딩·검색·생성·전체, ms)을 남겨 나중에 /logs
    # API로 다시 볼 수 있게 한다.
    # user_id는 ondelete="SET NULL": 사용자를 지워도 질문 기록 자체는 남긴다.
    op.create_table(
        "query_logs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "user_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("question", sa.Text, nullable=False),
        sa.Column("answer", sa.Text, nullable=False),
        sa.Column("retrieved_chunks", JSONB, nullable=False),
        sa.Column("model_name", sa.String(100), nullable=True),
        sa.Column("prompt_tokens", sa.Integer, nullable=True),
        sa.Column("completion_tokens", sa.Integer, nullable=True),
        sa.Column("embedding_latency_ms", sa.Integer, nullable=True),
        sa.Column("retrieval_latency_ms", sa.Integer, nullable=True),
        sa.Column("generation_latency_ms", sa.Integer, nullable=True),
        sa.Column("total_latency_ms", sa.Integer, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    # 되돌리기: 외래 키로 다른 테이블을 참조하는 쪽(query_logs, chunks)부터, 만든 순서의 반대로 지운다.
    # 확장(vector, pgcrypto)은 지우지 않는다.
    op.drop_table("query_logs")
    op.execute("DROP INDEX IF EXISTS chunks_embedding_hnsw_idx")
    op.drop_table("chunks")
    op.drop_index("ix_documents_source_path", table_name="documents")
    op.drop_table("documents")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

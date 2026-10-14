# [파일 역할] chunks 테이블의 ORM 모델. 검색의 기본 단위인 '청크'(문서를 잘게 나눈 조각)마다 본문, 헤딩 경로,
# 토큰 수, 언어, 임베딩 벡터, 전문 검색용 tsvector를 담는다.
# [연결] 수집(app/services/ingestion.py)이 행을 만들고, 검색(app/services/retrieval.py)이 벡터·BM25 질의로
# 읽는다. 스키마는 alembic/versions/0001~0004와 같아야 한다(스키마를 바꿀 때는 모델과 마이그레이션을 함께
# 고친다).
# [주의] 테스트는 이 모델로 create_all을 하므로, 여기 선언한 인덱스(GIN)만 테스트 DB에 생긴다. 언어별 HNSW
# 인덱스는 마이그레이션 0004에만 있다.

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

# Vector: pgvector의 vector(n) 열 타입. Computed: DB가 계산해 저장하는 생성 열. TSVECTOR: PostgreSQL 전문 검색
# 타입. TYPE_CHECKING 블록은 타입 힌트용으로만 Document를 가져와 순환 import를 피한다.
from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    Computed,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import TSVECTOR, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.document import Document

# 임베딩 열 차원(384). 영어 bge-small-en-v1.5의 출력 크기이고, 한국어 모델도 이 크기에 맞춘다.
# app/services/embedding.py가 이 값으로 모델 출력 차원을 검사하고, Granite R2 311M처럼 더 큰 모델은 이 길이로
# 잘라(truncate_dim) 쓴다. 바꾸려면 마이그레이션과 전체 재임베딩이 필요하다.
EMBEDDING_DIM = 384  # BAAI/bge-small-en-v1.5의 출력 차원


# 청크 한 행 = 한 문서의 chunk_index번째 조각.
class Chunk(Base):
    __tablename__ = "chunks"
    # (document_id, chunk_index) 유일 제약과 content_tsv의 GIN 인덱스. 마이그레이션 0001·0002와 같은 정의를
    # 모델에도 적어, create_all로 만든 테스트 스키마에서도 BM25 질의가 같은 인덱스 구조로 돈다.
    __table_args__ = (
        UniqueConstraint("document_id", "chunk_index"),
        Index("ix_chunks_content_tsv", "content_tsv", postgresql_using="gin"),
    )

    # 기본 키는 DB가 gen_random_uuid()로 만든다. 앱이 flush하면 값이 채워진다.
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    # 소속 문서. ondelete="CASCADE"라 문서 행을 지우면 DB가 청크도 지운다. 수집이 사라진 문서를 delete 문으로
    # 한꺼번에 지울 때(ORM 객체를 읽지 않음) 청크 정리를 이 DB 규칙에 맡긴다.
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False
    )
    # chunk_index: 문서 안 순번(0부터). heading_path: '페이지 제목 > 절 > 소절' 형태의 위치로, 인용 표시와
    # 임베딩 머리말에 쓴다. token_count: BM25의 문서 길이 정규화에 쓰는 토큰 수.
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    heading_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[int] = mapped_column(Integer, nullable=False)
    # 청크가 어느 번역 문서에서 왔는지("en", "ko"). 검색은 한 번에 한 언어 안에서만 한다. 문서 테이블이 아니라
    # 청크에 두어 벡터 질의와 BM25 질의가 조인 없이 언어로 거를 수 있게 한다.
    language: Mapped[str] = mapped_column(String(8), nullable=False, server_default="en")
    # 정규화된 임베딩 벡터. 같은 language의 청크끼리만 같은 모델로 만든 벡터라 비교할 수 있다.
    embedding: Mapped[list[float]] = mapped_column(Vector(EMBEDDING_DIM), nullable=False)
    # Postgres가 heading_path + content에 맞춰 늘 다시 계산하는 생성 열이라 앱은 이 열에 값을 쓰지 않는다.
    # 생성 열 식은 마이그레이션 0002와 글자 그대로 같아야 한다. 'english' 설정이라 영어 형태소 기준으로
    # 어휘소를 만든다.
    content_tsv: Mapped[str] = mapped_column(
        TSVECTOR,
        Computed("to_tsvector('english', coalesce(heading_path, '') || ' ' || content)", persisted=True),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # Document.chunks와 짝을 이루는 양방향 관계.
    document: Mapped["Document"] = relationship(back_populates="chunks")

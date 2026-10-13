# [파일 역할] documents 테이블의 ORM 모델. 수집한 마크다운 파일(FastAPI 문서 한 페이지) 하나가 한 행이다.
# [연결] 수집(app/services/ingestion.py)이 content_hash로 바뀐 문서만 골라 다시 처리하고, 문서 목록
# API(app/routers/documents.py)가 청크 수와 함께 보여 준다. 검색 결과의 인용에는 source_path가 나간다.

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.chunk import Chunk


# - source_path: 저장소 안 경로(예: docs/ko/docs/tutorial/handling-errors.md). 문서의 자연 키라 unique이고,
#   수집이 이 값으로 기존 행을 찾으므로 인덱스를 둔다. 경로 앞부분(docs/<언어>/docs/)이 언어를 나타낸다.
# - title: 첫 번째 '# ' 헤딩에서 뽑은 페이지 제목(없으면 경로).
# - source_commit_sha: 이 내용을 가져온 tiangolo/fastapi 커밋.
# - content_hash: SHA-256(청커 버전 + 임베딩 모델 식별자 + 원문). 같으면 재수집 때 건너뛴다. 청커나 모델이
#   바뀌어도 해시가 달라지게 한 이유는 docs/experiments.md v1→v3, v8에 있다.
# - fetched_at: 마지막으로 처리한 시각(갱신될 때 수집이 now()로 바꾼다).
class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    source_path: Mapped[str] = mapped_column(String(512), unique=True, nullable=False, index=True)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_commit_sha: Mapped[str] = mapped_column(String(40), nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # ORM 수준의 일대다 관계. cascade="all, delete-orphan"이라 세션에서 Document 객체를 지우거나 목록에서 뺀
    # 청크는 함께 지워진다. (DB 수준에서는 chunks.document_id의 ON DELETE CASCADE가 같은 역할을 한다.)
    chunks: Mapped[list["Chunk"]] = relationship(
        back_populates="document", cascade="all, delete-orphan"
    )

# [파일 역할] query_logs 테이블의 ORM 모델. /query/ask 한 번마다 질문, 답변, 검색된 청크, 모델 이름, 토큰 수,
# 단계별 지연을 한 행으로 남긴다.
# [왜 필요한가] README '한눈에 보기'에 적힌 대로 질문마다 검색 결과와 단계별 지연을 기록해, 나중에 /logs API와
# 채팅 화면의 '최근 질문'으로 다시 보거나 어느 단계가 느렸는지 확인할 수 있게 한다.
# [연결] app/routers/query.py가 쓰고, app/routers/logs.py가 본인 기록만 읽는다.

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


# 질문 기록 한 행.
class QueryLog(Base):
    __tablename__ = "query_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    # 질문한 사용자. 사용자가 지워지면 DB가 NULL로 바꿔(SET NULL) 기록은 남긴다. 그래서 nullable이다.
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    # retrieved_chunks: 검색된 청크 목록(JSONB). 항목마다 chunk_id, document_id, source_path, score,
    # cited(답변이 인용했는지)가 들어간다. 질문 시점의 검색 결과를 통째로 저장하므로, 나중에 재수집으로 청크가
    # 바뀌어도 그때 어떤 문서가 몇 점으로 검색됐는지는 남는다.
    # model_name·토큰 수: 생성기가 돌려준 값(GenerationResult). 열은 nullable이지만 지금 두 생성기는 모두
    # 정수를 채운다. Ollama 경로는 답변·인용 호출(가드 재생성 포함)의 토큰 수를 더한 값이다.
    # *_latency_ms: Stopwatch로 잰 임베딩·검색(재정렬 포함)·생성 단계 시간과 그 합(ms).
    retrieved_chunks: Mapped[list[dict]] = mapped_column(JSONB, nullable=False)
    model_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    prompt_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    completion_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    embedding_latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    retrieval_latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    generation_latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

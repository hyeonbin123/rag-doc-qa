# [파일 역할] 질문 기록 API(/logs, /logs/{id})의 응답 모양(app/routers/logs.py). 목록에는 요약만, 단건
# 조회에는 검색 결과와 단계별 지연까지 담는다.

import uuid
from datetime import datetime

from pydantic import BaseModel


# 목록용 요약: 질문, 답변, 전체 지연, 시각. 채팅 화면이 로그인할 때 최근 질문을 불러오는 데 쓴다.
# from_attributes=True로 ORM QueryLog 객체를 그대로 변환한다.
class QueryLogSummary(BaseModel):
    id: uuid.UUID
    question: str
    answer: str
    total_latency_ms: int | None
    created_at: datetime

    model_config = {"from_attributes": True}


# 단건 상세: 요약에 더해 검색된 청크 목록(JSON), 모델 이름, 토큰 수, 단계별 지연을 돌려준다. 요약을 상속해
# 공통 필드를 다시 적지 않는다.
class QueryLogDetail(QueryLogSummary):
    retrieved_chunks: list[dict]
    model_name: str | None
    prompt_tokens: int | None
    completion_tokens: int | None
    embedding_latency_ms: int | None
    retrieval_latency_ms: int | None
    generation_latency_ms: int | None

# [파일 역할] 질문 기록 API(/logs, /logs/{id})의 응답 모양(app/routers/logs.py). 목록은 기본이 요약이고,
# detail=true인 목록과 단건 조회는 검색 결과와 단계별 지연까지 담는 상세다.

import uuid
from datetime import datetime

from pydantic import BaseModel


# 목록용 요약(GET /logs 기본 응답): 질문, 답변, 전체 지연, 시각. 필드나 순서를 바꾸면 기본 목록 응답의
# 바이트가 바뀌어 이 목록을 읽는 클라이언트에 영향이 간다(tests/test_logs.py가 고정).
# from_attributes=True로 ORM QueryLog 객체를 그대로 변환한다.
class QueryLogSummary(BaseModel):
    id: uuid.UUID
    question: str
    answer: str
    total_latency_ms: int | None
    created_at: datetime

    model_config = {"from_attributes": True}


# 상세(GET /logs/{id}와 GET /logs?detail=true의 항목): 요약에 더해 검색된 청크 목록(JSON), 모델 이름,
# 토큰 수, 단계별 지연을 돌려준다. 채팅 화면은 detail=true 목록 하나로 최근 질문의 인용과 걸린 시간을
# 그린다. 요약을 상속해 공통 필드를 다시 적지 않는다.
class QueryLogDetail(QueryLogSummary):
    retrieved_chunks: list[dict]
    model_name: str | None
    prompt_tokens: int | None
    completion_tokens: int | None
    embedding_latency_ms: int | None
    retrieval_latency_ms: int | None
    generation_latency_ms: int | None

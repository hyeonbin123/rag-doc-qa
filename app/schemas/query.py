# [파일 역할] 핵심 API POST /query/ask의 요청·응답 모양(app/routers/query.py). 질문, 가져올 청크 수, 검색할
# 문서 언어를 받고, 답변·인용·질문 기록 id·단계별 지연을 돌려준다.

import uuid
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.text import NulFreeStr


# 질문 요청.
# - question: 1~2000자. NulFreeStr이라 NUL 문자가 있으면 생성까지 가기 전에 422로 거부한다(예전에는 LLM 답변을
#   다 만든 뒤 질문 기록을 저장할 때 500이 났음, ZAP 1차 지적).
# - top_k: LLM에 넘길 청크 수(1~10, 기본 5). 평가에서 모델은 상위 5개를 모두 읽는다는 전제로 Hit@5를 본다.
# - language: auto면 한글이 한 글자라도 있을 때 ko로 판별한다(app/services/language.py). en/ko로 직접 지정할
#   수도 있다.
class AskRequest(BaseModel):
    question: NulFreeStr = Field(min_length=1, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=10)
    language: Literal["auto", "en", "ko"] = Field(
        default="auto",
        description="Which docs translation to search. auto picks ko when the question contains Hangul.",
    )


# 답변이 근거로 쓴 청크 하나. 생성기가 고른 [N] 번호를 실제 청크로 바꾼 것이다. source_path와 heading_path는
# 채팅 화면이 공식 문서 링크와 절 이름을 보여 주는 데 쓴다. score는 검색 점수다(dense·hybrid는 코사인 유사도,
# rerank는 cross-encoder의 관련도 확률).
class Citation(BaseModel):
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    source_path: str
    heading_path: str | None
    score: float


# 단계별 걸린 시간(ms). retrieval에는 rerank 모드의 재정렬 시간도 들어간다. total은 세 단계의 합이다(질문 기록
# 저장 시간은 빠짐).
class LatencyBreakdown(BaseModel):
    embedding: int
    retrieval: int
    generation: int
    total: int


# 질문 응답. query_log_id로 /logs/{id}를 부르면 이 요청의 검색 결과 전체를 다시 볼 수 있다.
class AskResponse(BaseModel):
    answer: str
    citations: list[Citation]
    query_log_id: uuid.UUID
    latency_ms: LatencyBreakdown

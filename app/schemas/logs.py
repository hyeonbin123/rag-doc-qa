import uuid
from datetime import datetime

from pydantic import BaseModel


class QueryLogSummary(BaseModel):
    id: uuid.UUID
    question: str
    answer: str
    total_latency_ms: int | None
    created_at: datetime

    model_config = {"from_attributes": True}


class QueryLogDetail(QueryLogSummary):
    retrieved_chunks: list[dict]
    model_name: str | None
    prompt_tokens: int | None
    completion_tokens: int | None
    embedding_latency_ms: int | None
    retrieval_latency_ms: int | None
    generation_latency_ms: int | None

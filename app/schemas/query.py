import uuid

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=10)


class Citation(BaseModel):
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    source_path: str
    heading_path: str | None
    score: float


class LatencyBreakdown(BaseModel):
    embedding: int
    retrieval: int
    generation: int
    total: int


class AskResponse(BaseModel):
    answer: str
    citations: list[Citation]
    query_log_id: uuid.UUID
    latency_ms: LatencyBreakdown

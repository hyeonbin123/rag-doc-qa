import uuid
from datetime import datetime

from pydantic import BaseModel


class IngestRequest(BaseModel):
    commit_sha: str | None = None
    limit: int | None = None
    dry_run: bool = False


class IngestResult(BaseModel):
    documents_processed: int
    chunks_created: int
    chunks_updated: int
    chunks_skipped: int
    elapsed_ms: int


class DocumentOut(BaseModel):
    id: uuid.UUID
    source_path: str
    title: str | None
    chunk_count: int
    fetched_at: datetime

    model_config = {"from_attributes": True}

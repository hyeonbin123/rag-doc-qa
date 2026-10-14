# [파일 역할] 문서 API의 요청·응답 모양. 관리자 적재 요청(IngestRequest)과 결과(IngestResult), 문서 목록
# 항목(DocumentOut)을 정한다(app/routers/documents.py).

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

# NulFreeStr: DB에 저장되는 문자열에서 NUL(U+0000)을 422로 거부하는 타입(app/schemas/text.py).
from app.schemas.text import NulFreeStr


# 관리자 적재 요청.
# - commit_sha: 가져올 tiangolo/fastapi 커밋. 없으면 master의 최신 커밋. 문서마다 source_commit_sha로
#   저장되므로 NUL을 막는다.
# - limit: 앞에서 n개 문서만 처리(시험용). limit이 있으면 사라진 문서 삭제를 하지
#   않는다(app/services/ingestion.py).
# - dry_run: DB를 바꾸지 않고 처리할 문서·청크 수와 지울 문서 수만 센다.
class IngestRequest(BaseModel):
    commit_sha: NulFreeStr | None = None
    limit: int | None = None
    dry_run: bool = False


# 적재 결과 요약. documents_deleted는 트리에서 사라져 지운 문서 수다(전에 없던 필드라 기본값 0).
# chunks_skipped는 해시가 같아 건너뛴 '문서' 수를 센다(이름과 달리 청크 수가 아님, ingestion.py에서 문서마다
# 1씩 더함). 응답 필드 이름을 바꾸면 API를 쓰는 쪽이 깨지므로 이름은 두고, OpenAPI 설명에 뜻을 적는다.
# elapsed_ms는 전체 소요 시간.
class IngestResult(BaseModel):
    documents_processed: int
    documents_deleted: int = 0
    chunks_created: int
    chunks_updated: int
    chunks_skipped: int = Field(
        description="내용 해시가 바뀌지 않아 건너뛴 문서 수. 이름과 달리 청크 수가 아니라 문서 수를 센다."
    )
    elapsed_ms: int


# /documents 응답 항목: 문서 정보와 청크 수. chunk_count는 테이블 열이 아니라 라우터가 집계해 채운다.
class DocumentOut(BaseModel):
    id: uuid.UUID
    source_path: str
    title: str | None
    chunk_count: int
    fetched_at: datetime

    model_config = {"from_attributes": True}

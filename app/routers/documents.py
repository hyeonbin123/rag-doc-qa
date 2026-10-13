# [파일 역할] 문서 관련 API. 관리자 적재(POST /admin/documents/ingest)와 적재된 문서 목록·단건 조회(GET
# /documents, /documents/{id}).
# [연결] 적재 로직 자체는 app/services/ingestion.py의 run_ingestion에 있고, 같은 함수를
# CLI(scripts/ingest_fastapi_docs.py)도 쓴다. 이 라우터는 HTTP 입력·출력만 맡는다.

import uuid
from collections.abc import Callable

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies import get_embedder, require_admin_token
from app.models.chunk import Chunk
from app.models.document import Document
from app.schemas.document import DocumentOut, IngestRequest, IngestResult
from app.services.embedding import EmbeddingService
from app.services.ingestion import run_ingestion
from app.services.language import Language

# prefix 없이 경로를 각각 적는다(관리자 경로와 공개 경로의 앞부분이 다르다).
router = APIRouter(tags=["documents"])


# 관리자 적재. dependencies=[Depends(require_admin_token)]로 X-Admin-Token 헤더가 맞아야만 실행된다.
# GitHub에서 문서를 받아 청킹·임베딩 후 DB에 넣고, 전체 적재면 사라진 문서도 지운다.
# 문서 언어마다 다른 임베딩 모델을 쓰므로 모델 하나가 아니라 '언어 → 모델' 함수(embedder_for)를 넘긴다.
# 임베딩은 run_ingestion 안에서 모델 스레드로 돌아, 적재하는 동안에도 서버가 다른 요청에 답한다.
# 적재는 몇 분 걸릴 수 있는데 요청 하나 안에서 끝까지 한다(백그라운드 잡 큐는 README '하지 않은 것'에 있다).
@router.post(
    "/admin/documents/ingest",
    response_model=IngestResult,
    dependencies=[Depends(require_admin_token)],
)
async def ingest_documents(
    payload: IngestRequest,
    db: AsyncSession = Depends(get_db),
    embedder_for: Callable[[Language], EmbeddingService] = Depends(get_embedder),
) -> IngestResult:
    outcome = await run_ingestion(
        db,
        embedder_for,
        commit_sha=payload.commit_sha,
        limit=payload.limit,
        dry_run=payload.dry_run,
    )
    # 내부 결과(IngestOutcome)에서 API로 보일 필드만 골라 응답 모델로 옮긴다(commit_sha는 응답에 넣지 않는다).
    return IngestResult(
        documents_processed=outcome.documents_processed,
        documents_deleted=outcome.documents_deleted,
        chunks_created=outcome.chunks_created,
        chunks_updated=outcome.chunks_updated,
        chunks_skipped=outcome.chunks_skipped,
        elapsed_ms=outcome.elapsed_ms,
    )


# 적재된 문서 전체 목록과 문서별 청크 수. 인증 없이 열려 있다.
# 청크 수는 문서마다 따로 세지 않고(문서 수만큼 질의가 늘어나는 N+1 방지) chunks를 document_id로 묶어 센 부분
# 질의를 한 번 만들어 붙인다. outer join + coalesce라 청크가 0개인 문서도 0으로 나온다. 경로 순으로 정렬한다.
@router.get("/documents", response_model=list[DocumentOut])
async def list_documents(db: AsyncSession = Depends(get_db)) -> list[DocumentOut]:
    chunk_count_subq = (
        select(Chunk.document_id, func.count(Chunk.id).label("chunk_count"))
        .group_by(Chunk.document_id)
        .subquery()
    )
    result = await db.execute(
        select(Document, func.coalesce(chunk_count_subq.c.chunk_count, 0))
        .outerjoin(chunk_count_subq, chunk_count_subq.c.document_id == Document.id)
        .order_by(Document.source_path)
    )
    return [
        DocumentOut(
            id=doc.id,
            source_path=doc.source_path,
            title=doc.title,
            chunk_count=count,
            fetched_at=doc.fetched_at,
        )
        for doc, count in result.all()
    ]


# 문서 하나와 그 청크 수. 경로 매개변수를 uuid.UUID로 받아, UUID가 아닌 값은 DB까지 가지 않고 422가 된다.
# 없으면 404.
@router.get("/documents/{document_id}", response_model=DocumentOut)
async def get_document(document_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> DocumentOut:
    document = await db.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    chunk_count = await db.scalar(
        select(func.count(Chunk.id)).where(Chunk.document_id == document.id)
    )
    return DocumentOut(
        id=document.id,
        source_path=document.source_path,
        title=document.title,
        chunk_count=chunk_count or 0,
        fetched_at=document.fetched_at,
    )

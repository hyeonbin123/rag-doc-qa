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

router = APIRouter(tags=["documents"])


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
    return IngestResult(
        documents_processed=outcome.documents_processed,
        chunks_created=outcome.chunks_created,
        chunks_updated=outcome.chunks_updated,
        chunks_skipped=outcome.chunks_skipped,
        elapsed_ms=outcome.elapsed_ms,
    )


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


@router.get("/documents/{document_id}", response_model=DocumentOut)
async def get_document(document_id: str, db: AsyncSession = Depends(get_db)) -> DocumentOut:
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

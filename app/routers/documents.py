# [파일 역할] 문서 관련 API. 관리자 적재(POST /admin/documents/ingest)와 적재된 문서 목록·단건 조회(GET
# /documents, /documents/{id}).
# [연결] 적재 로직 자체는 app/services/ingestion.py의 run_ingestion에 있고, 같은 함수를
# CLI(scripts/ingest_fastapi_docs.py)도 쓴다. 이 라우터는 HTTP 입력·출력만 맡는다.

import logging
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
from app.services.ingestion import (
    DocsSourceUnavailable,
    IngestionAlreadyRunning,
    UnknownDocsRef,
    run_ingestion,
)
from app.services.language import Language

# prefix 없이 경로를 각각 적는다(관리자 경로와 공개 경로의 앞부분이 다르다).
router = APIRouter(tags=["documents"])

# 이 모듈의 로그(GitHub 장애로 적재가 멈춘 한 줄). configure_logging의 형식으로 'app.routers.documents' 이름이
# 찍힌다.
logger = logging.getLogger(__name__)

# 요청의 commit_sha를 GitHub가 모를 때의 422 본문 항목. 요청 본문 검증 오류(app/main.py의 422 처리기가
# 만드는 type·loc·msg 항목)와 같은 꼴로 두어, 클라이언트가 같은 방식으로 '어느 필드가 틀렸는지'를 읽게 한다.
# 보낸 값은 다른 422와 마찬가지로 되돌려 주지 않는다. 응답으로 그대로 나가는 글이라 영어로 둔다.
UNKNOWN_DOCS_REF_ERROR = {
    "type": "unknown_docs_ref",
    "loc": ["body", "commit_sha"],
    "msg": "GitHub does not know this ref",
}


# 관리자 적재. dependencies=[Depends(require_admin_token)]로 X-Admin-Token 헤더가 맞아야만 실행된다.
# GitHub에서 문서를 받아 청킹·임베딩 후 DB에 넣고, 전체 적재면 사라진 문서도 지운다. 요청 본문(commit_sha의
# ref 형식, limit ≥ 1)은 IngestRequest가 검사해 어긋나면 422다.
# 문서 언어마다 다른 임베딩 모델을 쓰므로 모델 하나가 아니라 '언어 → 모델' 함수(embedder_for)를 넘긴다.
# 임베딩은 run_ingestion 안에서 모델 스레드로, 청킹과 GitHub 클라이언트 생성은 Starlette 스레드 풀로 돌아
# 적재하는 동안에도 서버가 다른 요청에 답한다.
# 적재는 몇 분 걸릴 수 있는데 요청 하나 안에서 끝까지 한다(백그라운드 잡 큐는 README '하지 않은 것'에 있다).
# 같은 DB에서 다른 적재(이 API의 다른 요청이나 CLI)가 진행 중이면 409다.
# GitHub 쪽 실패(2026-11-05, 그 전에는 모두 500): 요청이 준 commit_sha를 GitHub가 모르면 422(위 검증 오류와
# 같은 꼴의 항목), GitHub에 닿지 못하거나 GitHub가 오류 상태로 답하면 502다. 어느 쪽이든 적재의 네트워크
# 단계에서 멈춰 DB에는 아무것도 쓰지 않았다. commit_sha를 주지 않았는데 서버 기본
# ref(FASTAPI_DOCS_COMMIT_SHA)를 GitHub가 모르면(UnknownConfiguredDocsRef) 요청을 고쳐서 풀릴 일이 아닌 서버
# 설정 오류라 잡지 않고 500으로 둔다(서버 로그에 설정 이름이 든 트레이스백이 남는다).
# responses의 설명은 OpenAPI 문서(/docs)에 그대로 나가는 글이라 다른 라우터(auth의 가입 409)처럼 영어로 둔다.
# 422를 여기 적으면 FastAPI가 자동으로 붙이던 422 항목을 대신하므로, 자동 항목과 같은 검증 오류
# 스키마(HTTPValidationError)를 직접 가리킨다(위 본문 항목도 그 스키마의 꼴이다. tests/test_documents.py가
# 확인한다).
@router.post(
    "/admin/documents/ingest",
    response_model=IngestResult,
    dependencies=[Depends(require_admin_token)],
    responses={
        status.HTTP_409_CONFLICT: {"description": "Ingestion already running"},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "Validation Error, or a commit_sha that GitHub does not know",
            "content": {"application/json": {"schema": {"$ref": "#/components/schemas/HTTPValidationError"}}},
        },
        status.HTTP_502_BAD_GATEWAY: {
            "description": "GitHub could not be reached or answered with an error; nothing was ingested"
        },
    },
)
async def ingest_documents(
    payload: IngestRequest,
    db: AsyncSession = Depends(get_db),
    embedder_for: Callable[[Language], EmbeddingService] = Depends(get_embedder),
) -> IngestResult:
    try:
        outcome = await run_ingestion(
            db,
            embedder_for,
            commit_sha=payload.commit_sha,
            limit=payload.limit,
            dry_run=payload.dry_run,
        )
    except IngestionAlreadyRunning as exc:
        # 다른 적재가 어드바이저리 잠금을 쥔 상태. 아무것도 하지 않았음을 409로 알린다(예전에는 둘 다 돌다가
        # 늦은 쪽이 먼저 쪽의 commit을 몇 분 기다린 뒤 유일 제약 위반 500으로 끝났다,
        # app/services/ingestion.py 주석).
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="ingestion already running") from exc
    except UnknownDocsRef as exc:
        # 요청이 준 ref를 GitHub가 모른다(commits API 404·422). 요청을 고치면 되는 오류라 422로 알린다.
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=[UNKNOWN_DOCS_REF_ERROR]
        ) from exc
    except DocsSourceUnavailable as exc:
        # GitHub 장애(연결 실패·시간 초과·5xx·요청 한도 초과 등). 원인(요청 주소와 상태)은 응답에 싣지 않고
        # 서버 로그 한 줄에만 남긴다. 운영자는 이 줄로 '우리 버그(500)'와 '상류 장애(502)'를 가른다.
        logger.warning("admin ingestion stopped, docs source unavailable: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail="docs source unavailable"
        ) from exc
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

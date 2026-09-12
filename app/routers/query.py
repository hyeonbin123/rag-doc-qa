from collections.abc import Callable

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.core.timing import Stopwatch
from app.db.session import get_db
from app.dependencies import get_current_user, get_embedder, get_generator, get_reranker
from app.models.query_log import QueryLog
from app.models.user import User
from app.schemas.query import AskRequest, AskResponse, Citation, LatencyBreakdown
from app.services.embedding import EmbeddingService
from app.services.generation import GenerationService
from app.services.language import Language, detect_language
from app.services.reranking import RerankerService
from app.services.retrieval import retrieve

router = APIRouter(prefix="/query", tags=["query"])


@router.post("/ask", response_model=AskResponse)
async def ask(
    payload: AskRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    embedder_for: Callable[[Language], EmbeddingService] = Depends(get_embedder),
    generator: GenerationService = Depends(get_generator),
    reranker_for: Callable[[Language], RerankerService] | None = Depends(get_reranker),
    settings: Settings = Depends(get_settings),
) -> AskResponse:
    language = (
        detect_language(payload.question) if payload.language == "auto" else payload.language
    )
    embed_sw = Stopwatch()
    with embed_sw.measure():
        query_embedding = embedder_for(language).embed_query(payload.question)

    retrieval_sw = Stopwatch()
    with retrieval_sw.measure():  # includes cross-encoder reranking in "rerank" mode
        retrieved = await retrieve(
            db,
            payload.question,
            query_embedding,
            payload.top_k,
            settings.retrieval_mode,
            language=language,
            reranker=reranker_for(language) if reranker_for else None,
        )

    generation_sw = Stopwatch()
    with generation_sw.measure():
        generation_result = await generator.answer(payload.question, retrieved, language=language)

    total_ms = embed_sw.elapsed_ms + retrieval_sw.elapsed_ms + generation_sw.elapsed_ms

    cited_indices = {n - 1 for n in generation_result.cited_chunk_numbers}
    retrieved_chunks_json = [
        {
            "chunk_id": str(chunk.chunk_id),
            "document_id": str(chunk.document_id),
            "source_path": chunk.source_path,
            "score": chunk.score,
            "cited": idx in cited_indices,
        }
        for idx, chunk in enumerate(retrieved)
    ]

    query_log = QueryLog(
        user_id=current_user.id,
        question=payload.question,
        answer=generation_result.answer,
        retrieved_chunks=retrieved_chunks_json,
        model_name=generation_result.model_name,
        prompt_tokens=generation_result.input_tokens,
        completion_tokens=generation_result.output_tokens,
        embedding_latency_ms=embed_sw.elapsed_ms,
        retrieval_latency_ms=retrieval_sw.elapsed_ms,
        generation_latency_ms=generation_sw.elapsed_ms,
        total_latency_ms=total_ms,
    )
    db.add(query_log)
    await db.commit()
    await db.refresh(query_log)

    citations = [
        Citation(
            chunk_id=chunk.chunk_id,
            document_id=chunk.document_id,
            source_path=chunk.source_path,
            heading_path=chunk.heading_path,
            score=chunk.score,
        )
        for idx, chunk in enumerate(retrieved)
        if idx in cited_indices
    ]

    return AskResponse(
        answer=generation_result.answer,
        citations=citations,
        query_log_id=query_log.id,
        latency_ms=LatencyBreakdown(
            embedding=embed_sw.elapsed_ms,
            retrieval=retrieval_sw.elapsed_ms,
            generation=generation_sw.elapsed_ms,
            total=total_ms,
        ),
    )

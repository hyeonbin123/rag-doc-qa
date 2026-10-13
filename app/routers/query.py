# [파일 역할] 이 서비스의 핵심 API POST /query/ask. 질문 하나를 받아 RAG 파이프라인 전체를 한 번 돈다.
# [흐름] 질문 언어 판별 → 그 언어의 모델로 질문 임베딩(모델 스레드) → 같은 언어 청크에서 검색(RETRIEVAL_MODE:
# dense / hybrid / rerank) → 읽기 트랜잭션 종료 → LLM 답변·인용 생성 → 질문 기록 저장 → 답변·인용·단계별 지연
# 응답.
# [설계 포인트] 모델 계산은 이벤트 루프 밖(run_model)에서 하고, LLM을 기다리는 동안에는 DB 연결을 잡지 않는다.
# 각 단계 시간을 Stopwatch로 따로 재서 응답과 기록에 남긴다.
# [연결] 의존성은 app/dependencies.py, 검색은 app/services/retrieval.py, 생성은 app/services/generation.py.

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
from app.services.inference import run_model
from app.services.language import Language, detect_language
from app.services.reranking import RerankerService
from app.services.retrieval import retrieve, score_floor_for

router = APIRouter(prefix="/query", tags=["query"])


# 질문 하나에 답한다. 로그인이 필요하고(get_current_user), 임베딩·생성·재정렬 모델은 의존성으로 주입받아
# 테스트에서 가짜로 바꿀 수 있다. reranker_for는 rerank 모드가 아니면 None이다.
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
    # auto면 한글이 한 글자라도 있을 때 ko로 판별한다. 언어가 정해져야 어느 임베딩 모델과 어느 청크(언어별
    # 인덱스)를 쓸지 정할 수 있다. 두 모델의 벡터는 서로 다른 공간이라 질문도 반드시 문서와 같은 모델로
    # 임베딩해야 한다.
    language = (
        detect_language(payload.question) if payload.language == "auto" else payload.language
    )
    embedder = embedder_for(language)
    embed_sw = Stopwatch()
    with embed_sw.measure():
        # CPU-bound model call: queued on the model thread so other requests keep moving.
        query_embedding = await run_model(embedder.embed_query, payload.question)

    # 검색. score_floor는 임베딩 모델별 점수 바닥값으로, dense 검색에서 이보다 낮은 결과를 버려 문서가 다루지
    # 않는 질문에는 근거 청크가 붙지 않게 한다(app/services/retrieval.py).
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
            score_floor=score_floor_for(embedder.model_name),
        )

    # End the read transaction so the pooled connection isn't held while the LLM
    # generates (seconds per question, queued in Ollama). Commit rather than rollback:
    # rollback expires current_user, and reloading it later would need async IO.
    await db.commit()

    generation_sw = Stopwatch()
    with generation_sw.measure():
        generation_result = await generator.answer(payload.question, retrieved, language=language)

    # 전체 지연은 세 단계의 합이다. 중간 commit과 기록 저장 시간은 들어가지 않는다.
    total_ms = embed_sw.elapsed_ms + retrieval_sw.elapsed_ms + generation_sw.elapsed_ms

    # 생성기는 프롬프트의 [1], [2], ... 번호(1부터)로 인용을 돌려주므로 0부터 시작하는 목록 위치로 바꾼다.
    # 범위를 벗어난 번호는 아래에서 어떤 청크와도 맞지 않아 그냥 무시된다.
    # 질문 기록에는 검색된 청크 전체를 cited 표시와 함께 남겨, 무엇을 찾았고 그중 무엇을 썼는지 나중에 볼 수
    # 있게 한다.
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

    # 질문 기록을 짧은 새 트랜잭션으로 저장한다. refresh로 DB가 만든 id를 받아 응답의 query_log_id에 넣는다.
    # 질문 문자열은 AskRequest에서 NUL을 이미 걸렀으므로 여기서 그 때문에 PostgreSQL 오류가 나지는 않는다.
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

    # 응답의 인용은 검색 순서를 유지한 채 생성기가 인용한 청크만 남긴다.
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

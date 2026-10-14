"""전체 파이프라인 답변 평가: 키워드 커버리지 + LLM 판정(LLM-as-judge)의 충실도와 정확도.

모든 답을 먼저 생성해 문항별로 eval/runs/<tag>.gen.jsonl에 저장한다(청크 id와 본문이 붙은 순위별 문단, 답,
걸린 시간, 토큰 수). 그 뒤 판정 모델이 저장된 답을 채점하고, 판정 응답은
eval/runs/<tag>.<판정 라벨>.judge.jsonl에 간다. 여기에는 Ollama가 읽은 프롬프트 토큰 수와 모델 토크나이저로
센 토큰 수가 함께 들어가, 잘린 프롬프트가 문항마다 보인다. eval/run_judge.py는 저장된 답으로 판정만 다시
돌린다.

판정은 GENERATION_PROVIDER가 고른 제공자로 돌므로, 완전히 로컬(무료)에서 평가를 돌릴 수 있다.
--judge-model은 판정 모델을 하나로 고정해, 생성 모델을 비교하는 실행들이 모두 같은 판정 모델로 채점되게
한다. Ollama 판정은 truncate=false로 8192토큰 문맥을 요청한다(docs/experiments.md v11). --judge-num-ctx 0은
Ollama 기본 문맥에서 돌던 v11 이전 호출을 보낸다.

사용법:
    python -m eval.run_answer_eval [--top-k 5] [--tag v1_baseline] [--mode dense|hybrid|rerank] [--skip-judge]
        [--dataset eval/qa_test2.jsonl] [--judge-model qwen2.5:7b-instruct]
        [--judge-num-ctx 8192] [--judge-label J1] [--order dataset|shuffle] [--seed 20261003]
        [--no-token-count] [--cross-lingual] [--score-floor 0.3] [--no-vector-check]
"""

# [파일 역할] 답변 품질 평가의 본 스크립트. 질문셋의 문항마다 앱과 같은 경로(질문 언어 판별 → 같은 언어 모델로
# 질문 임베딩 → 검색 → 생성)로 답을 만들고, 그 기록을 남긴 뒤 LLM 판정으로 채점해 마크다운 리포트를 쓴다.
# [왜 이렇게 나눴나] v11에서 '모든 답 생성 → 기록 저장 → 일괄 판정'으로 바꿨다. 답과 패시지를 저장해 두면
# eval/run_judge.py로 생성 없이 다시 판정할 수 있고(판정 설정 비교, J0/J1), 생성과 판정을 번갈아 하면 Ollama가
# 모델을 계속 바꿔 올려 생성 시간에 그 시간이 섞이기 때문이다(docs/experiments.md v11).
# [흐름] main: 설정·생성기·토크나이저 준비 → 저장 벡터 확인(eval/retrieval_checks.py) → 문항별 generate_answer
# → <tag>.gen.jsonl과 .meta.json 저장 → (선택) judge_and_save로 판정 → eval/answer_report.render_report로
# 리포트.
# [연결] 판정 로직은 eval/judge.py, 판정 실행·기록은 eval/run_judge.py, 토크나이저는 eval/tokens.py, 두 팔
# 나누기는 eval/generator_arms.py가 이 파일의 기록을 읽는다. tests/test_answer_eval.py가
# generate_answer·generation_order·build_generator를 검증한다.

from __future__ import annotations

import argparse
import asyncio
import random
import sys
import time
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

# 앱 모듈(app.*)을 그대로 가져와 평가가 실제 서비스와 같은 설정·임베딩·검색·프롬프트를 쓰게 한다.
# _build_user_message와 system_prompt_for는 생성 프롬프트의 토큰 수를 앱과 같은 문장으로 세려고 가져온다.
# 평가 하네스 내부 모듈(eval.*): 리포트 렌더링, 데이터셋·기록 입출력, 판정 설정과 스키마, 저장 벡터 확인, 판정
# 실행·Ollama 상태 기록, 모델별 토크나이저.
from app.config import Settings, get_settings
from app.db.session import async_session_maker
from app.services.embedding import get_embedding_service
from app.services.generation import (
    KANA_HAN_RE,
    OLLAMA_ANSWER_PROMPT,
    GenerationService,
    OllamaGenerationService,
    _build_user_message,
    get_generation_service,
    system_prompt_for,
)
from app.services.language import Language, detect_language
from app.services.reranking import RerankerService, get_reranker_service
from app.services.retrieval import RetrievalMode, RetrievedChunk, page_key, retrieve, score_floor_for
from eval.answer_report import display_path, render_report
from eval.common import (
    DATASET_PATH,
    RUNS_DIR,
    EvalQuestion,
    git_commit,
    keyword_coverage,
    load_dataset,
    write_json,
    write_jsonl,
    write_report,
)
from eval.judge import DEFAULT_JUDGE_NUM_CTX, JUDGE_SCHEMA, JUDGE_TOOL, JudgeConfig, TokenCounter
from eval.retrieval_checks import check_stored_vectors
from eval.run_judge import default_label, judge_and_save, meta_path, model_digest, ollama_state
from eval.tokens import counter_for_model

# JUDGE_SCHEMA·JUDGE_TOOL·KANA_HAN_RE는 예전에 이 모듈에 정의돼 있다가 eval/judge.py와
# app/services/generation.py로 옮겨졌다. __all__에 남겨 이전 import 경로가 계속 동작하게 하고, 이 파일에서
# 직접 쓰지 않는 import가 린트(F401)에 걸리지 않게 한다.
__all__ = [
    "JUDGE_SCHEMA",
    "JUDGE_TOOL",
    "KANA_HAN_RE",
    "build_generator",
    "generate_answer",
    "generation_order",
    "keyword_coverage",
]

# KANA_HAN_RE: 가나(U+3040~U+30FF)와 한자(U+4E00~U+9FFF). 문서는 이 문자들을 쓰지 않으므로, 답에 나왔다면
# 모델이 일본어나 중국어로 샌 것이다(7B 모델의 한국어 답에서 봤다). 평가에서는 코드 부분까지 포함해 답
# 어디에서든 센다.

# 생성 프롬프트 토큰 수를 세는 함수의 타입: (질문, 검색된 청크, 언어) → 토큰 수.
GenerationPromptCounter = Callable[[str, list[RetrievedChunk], Language], int]


# 평가용 생성기를 만든다. Ollama가 아니면(예: Claude) 앱의 생성기를 그대로 쓴다.
# Ollama일 때는 앱과 같은 모델·think·언어 가드 설정으로 만들되 strict_citations=False를 준다. 앱은 인용 응답이
# JSON이 아니면 실패하지만, 평가는 그 문항을 기록하고 계속 가야 v13처럼 인용 스키마 오류 수를 셀 수 있기
# 때문이다.
def build_generator(settings: Settings) -> GenerationService:
    """설정된 생성기. Ollama면 잘못된 인용 응답을 기록하는 생성기를 만든다.

    앱은 JSON이 아닌 인용 응답에서 예외를 내지만, 평가 실행은 그것을 문항별로 기록하고(docs/experiments.md
    v13이 그 수를 센다) 계속 진행한다.
    """
    if settings.generation_provider != "ollama":
        return get_generation_service()
    return OllamaGenerationService(
        settings.ollama_base_url,
        settings.ollama_model_name,
        think=settings.ollama_think,
        language_guard=settings.language_guard,
        strict_citations=False,
    )


# 생성 순서를 정한다. 기본은 데이터셋 순서, --order shuffle이면 seed로 고정한 셔플 순서다.
# v11에서 '순서를 바꿔 다시 생성해도 답이 같은가'(생성 노이즈 M4)를 재려고 넣었다. 같은 seed면 항상 같은
# 순서가 나와 재현할 수 있다. 바뀌는 것은 생성 순서뿐이고, 기록·판정·리포트는 데이터셋 순서로 둔다.
def generation_order(n: int, order: str, seed: int) -> list[int]:
    """생성할 순서의 인덱스: 데이터셋 순서, 또는 seed로 고정한 셔플 순서."""
    indices = list(range(n))
    if order == "shuffle":
        random.Random(seed).shuffle(indices)
    return indices


# Ollama 답변 호출의 프롬프트(시스템 규칙 + 패시지 + 질문)를 토크나이저로 세는 함수를 만든다. 앱과 같은 시스템
# 프롬프트·사용자 메시지를 만들어 채팅 템플릿째 센다.
# 왜 세나: 생성 호출은 num_ctx 8192에서 truncate를 보내지 않으므로, 넘쳤다면 조용히 잘렸을 것이다. 문항마다
# 토큰 수를 남겨 그런 일이 없었는지 기록으로 확인한다(docs/experiments.md v11·v13 CPU 확인).
def ollama_answer_prompt_counter(count_tokens: TokenCounter) -> GenerationPromptCounter:
    """Ollama 답변 호출의 프롬프트(시스템 규칙 + 문단 + 질문)를 센다."""

    def count(question: str, chunks: list[RetrievedChunk], language: Language) -> int:
        return count_tokens(
            [
                {"role": "system", "content": system_prompt_for(OLLAMA_ANSWER_PROMPT, language)},
                {"role": "user", "content": _build_user_message(question, chunks)},
            ]
        )

    return count


# 문항 하나를 검색 → 생성하고, 판정과 분석에 필요한 모든 것을 dict 한 줄(gen.jsonl의 한 행)로 돌려준다.
# 입력의 embedder는 언어를 받아 그 언어의 임베딩 서비스를 돌려주는 함수다(앱처럼 질문마다 언어별 모델을
# 고르려고). count_generation_prompt가 없으면 토큰 수는 None으로 남긴다.
# 기록에는 검색된 청크의 id·순위·점수·본문까지 넣는다. 그래야 나중에 같은 패시지로 다시 판정하거나, 정답
# 페이지가 컨텍스트에 있었는지를 다시 셀 수 있다.
async def generate_answer(
    db,
    embedder,
    generator,
    q: EvalQuestion,
    top_k: int,
    mode: RetrievalMode,
    reranker: RerankerService | None,
    count_generation_prompt: GenerationPromptCounter | None = None,
    *,
    cross_lingual: bool = False,
    score_floor: float | None = None,
) -> dict:
    """답 하나를 검색·생성하고 기록한다.

    `cross_lingual`이면 한국어 질문이 영어 청크도 함께 검색한다(docs/experiments.md v12). 영어 질문은 언제나
    영어만 검색한다. `score_floor`의 기본값은 질문을 임베딩한 모델의 바닥값이다.
    """
    # 앱의 /query/ask와 같은 순서: 질문 언어 판별(한글이 있으면 ko) → 그 언어의 모델로 질문 임베딩. 교차언어
    # 검색은 한국어 질문에만 적용한다.
    language = detect_language(q.question)
    query_model = embedder(language)
    query_vector = query_model.embed_query(q.question)
    crossed = cross_lingual and language == "ko"
    # --score-floor를 주지 않으면 질문을 임베딩한 모델의 바닥값(SCORE_FLOORS, 없으면 0.3)을 써서 앱과 같게
    # 한다.
    floor = score_floor if score_floor is not None else score_floor_for(query_model.model_name)
    retrieved = await retrieve(
        db,
        q.question,
        query_vector,
        top_k,
        mode,
        language=language,
        reranker=reranker,
        score_floor=floor,
        cross_lingual=crossed,
    )
    # 생성 시간은 검색을 뺀 생성 호출만 잰다(Ollama 두 단계 호출과 언어 가드 재시도 포함). v10·v13의 생성 지연
    # 조건(중앙값 10초 이하)이 이 값을 쓴다. raw 팔에서는 eval/generator_arms.py가 재시도 시간을 뺀다.
    start = time.perf_counter()
    generation_result = await generator.answer(q.question, retrieved, language=language)
    generation_ms = (time.perf_counter() - start) * 1000
    # Ollama 생성기가 채워 주는 호출별 진단. 다른 프로바이더는 비어 있으므로 빈 dict로 다룬다.
    # unguarded_answer는 언어 가드가 다시 만들었을 때만 있는 첫 답이다.
    diagnostics = generation_result.diagnostics or {}
    unguarded = diagnostics.get("unguarded_answer")

    # 정답 페이지의 청크는 어느 번역이든 정답으로 센다(run_retrieval_eval과 같음).
    expected_pages = {page_key(p) for p in q.expected_source_paths}
    # 검색 결과 중 정답 페이지 청크가 처음 나온 순위. 컨텍스트에 정답이 있었는지 볼 때 쓴다(없으면 None).
    first_hit_rank = next(
        (
            rank
            for rank, chunk in enumerate(retrieved, start=1)
            if page_key(chunk.source_path) in expected_pages
        ),
        None,
    )
    return {
        "id": q.id,
        "question": q.question,
        "language": language,
        "reference_answer": q.reference_answer,
        "expected_source_paths": q.expected_source_paths,
        "must_include_keywords": q.must_include_keywords,
        "chunks": [
            {
                "rank": rank,
                "chunk_id": str(r.chunk_id),
                "source_path": r.source_path,
                "heading_path": r.heading_path,
                "score": round(float(r.score), 6),
                "content": r.content,
            }
            for rank, r in enumerate(retrieved, start=1)
        ],
        "first_hit_rank": first_hit_rank,
        "cross_lingual": crossed,
        "score_floor": floor,
        "answer": generation_result.answer,
        "cited_chunk_numbers": generation_result.cited_chunk_numbers,
        "generation_ms": generation_ms,
        # Ollama가 알려 준 두 호출(답변 + 인용)의 토큰 수 합.
        "generation_input_tokens": generation_result.input_tokens,
        "generation_output_tokens": generation_result.output_tokens,
        # 답변 호출의 프롬프트를 토크나이저로 센 수. 8191을 넘었다면 잘렸을 것이다.
        "generation_prompt_tokens_counted": (
            count_generation_prompt(q.question, retrieved, language) if count_generation_prompt else None
        ),
        # 판정과 무관한 두 지표: 기대 키워드가 답에 들어 있는 비율, 그리고 답 어디에든(코드 포함) 가나·한자가
        # 있는지(kana_han). kana_han은 v10~v13에서 '한국어 답에 일본어·중국어가 섞임'을 세는 결정 지표다.
        "keyword_coverage": keyword_coverage(generation_result.answer, q.must_include_keywords),
        "kana_han": bool(KANA_HAN_RE.search(generation_result.answer)),
        # v13: Ollama 제공자가 알려 주는 언어 가드 정보(다시 생성했으면 첫 답)와 호출별 세부 정보. 알려 주지
        # 않는 제공자에서는 None/False다.
        "guard_applied": bool(diagnostics.get("guard_applied")),
        "unguarded_answer": unguarded,
        "kana_han_unguarded": bool(KANA_HAN_RE.search(unguarded)) if unguarded is not None else None,
        "guard_retry_ms": diagnostics.get("guard_retry_ms"),
        "generation_calls": (
            {"answer": diagnostics["answer_calls"], "citation": diagnostics["citation_call"]}
            if "answer_calls" in diagnostics
            else None
        ),
        "citation_schema_error": diagnostics.get("citation_schema_error"),
        "citation_reply": diagnostics.get("citation_reply"),
        "think": diagnostics.get("think"),
        "think_tag_in_answer": diagnostics.get("think_tag_in_answer"),
    }


# 평가 한 번을 실행한다. 반환값은 판정 오류가 있으면 1, 없으면 0(명령의 종료 코드).
async def main(args: argparse.Namespace) -> int:
    settings = get_settings()
    mode = args.mode or settings.retrieval_mode
    embedder = get_embedding_service  # 언어별 조회 함수. 질문마다 그 질문의 언어로 부른다
    generator = build_generator(settings)
    questions = load_dataset(args.dataset)
    ollama = settings.generation_provider == "ollama"
    model_in_use = settings.ollama_model_name if ollama else settings.claude_model_name
    # --judge-model을 주지 않으면 생성 모델이 판정도 한다. v10부터는 생성 모델을 바꿔도 같은 채점자로
    # 비교하려고 판정 모델을 qwen2.5:7b-instruct로 고정해 넘긴다(README 평가 절).
    judge_model = args.judge_model or model_in_use
    # 토크나이저 수는 Ollama일 때만 센다(prompt_eval_count와 비교할 대상이 Ollama뿐이라서). 매핑된
    # 토크나이저가 없는 모델이면 counter_for_model이 None을 돌려준다.
    use_counter = ollama and not args.no_token_count
    gen_counter = counter_for_model(model_in_use) if use_counter else None
    judge_counter = counter_for_model(judge_model) if use_counter and not args.skip_judge else None

    # 교차언어 검색은 dense에만 구현돼 있으므로 다른 모드와 함께 주면 바로 멈춘다.
    if args.cross_lingual and mode != "dense":
        raise SystemExit("--cross-lingual is dense only")
    started = datetime.now(UTC).isoformat()
    # 셔플 순서로 생성해도 기록은 데이터셋 자리(index)에 넣어, 파일과 판정이 항상 데이터셋 순서가 되게 한다.
    records: list[dict] = [{} for _ in questions]
    vector_checks: list[dict] = []
    languages = sorted({detect_language(q.question) for q in questions})
    async with async_session_maker() as db:
        # 측정 전에 이 DB의 저장 벡터가 지금 설정된 모델로 만든 것인지 확인한다. 교차언어면 영어 청크도 한국어
        # 모델로 만든 것이어야 한다.
        if not args.no_vector_check:  # eval/retrieval_checks.py 참고
            for language in languages:
                vector_checks.append(await check_stored_vectors(db, embedder(language), language))
            if args.cross_lingual and "ko" in languages:
                vector_checks.append(await check_stored_vectors(db, embedder("ko"), "en"))
        for order_index, index in enumerate(generation_order(len(questions), args.order, args.seed)):
            q = questions[index]
            reranker = None
            # rerank 모드의 재정렬 모델도 언어마다 다르다(영어 MiniLM, 한국어 다국어 모델, docs/experiments.md
            # v9).
            if mode == "rerank":  # 임베딩 모델처럼 질문 언어로 고른다
                reranker = get_reranker_service(detect_language(q.question))
            record = await generate_answer(
                db,
                embedder,
                generator,
                q,
                args.top_k,
                mode,
                reranker,
                ollama_answer_prompt_counter(gen_counter) if gen_counter else None,
                cross_lingual=args.cross_lingual,
                score_floor=args.score_floor,
            )
            record.update(
                dataset=args.dataset.name,
                dataset_index=index,
                order_index=order_index,
                run_tag=args.tag,
                model=model_in_use,
                retrieval_mode=mode,
                top_k=args.top_k,
            )
            records[index] = record
            print(
                f"[generate {order_index + 1}/{len(questions)}] {q.id} "
                f"{record['generation_ms']:.0f} ms",
                flush=True,
            )

    # 문항별 생성 기록을 쓰고, 실행 조건을 옆의 .meta.json에 남긴다. 같은 태그로 다시 돌리면 덮어쓴다.
    # meta에는 날짜, 커밋, DB 이름, 언어별 임베딩 모델 identity, 벡터 확인 결과, Ollama 버전, 실행 직후
    # /api/ps(모델이 GPU에 다 올라갔는지 확인용), 모델 digest(태그만으로는 모델이 고정되지 않음), think·언어
    # 가드 설정이 들어간다.
    gen_path = RUNS_DIR / f"{args.tag}.gen.jsonl"
    write_jsonl(gen_path, records)
    state = await ollama_state(settings.ollama_base_url) if ollama else {}
    gen_meta = {
        "date": started,
        "tag": args.tag,
        "provider": settings.generation_provider,
        "model": model_in_use,
        "top_k": args.top_k,
        "retrieval_mode": mode,
        "cross_lingual": bool(args.cross_lingual),
        "score_floor": args.score_floor,
        # 접속 URL의 마지막 부분(DB 이름)만 남긴다. 복제 DB(ragdb_p1_<이름>) 중 어느 것을 쟀는지 알 수 있고,
        # URL 앞쪽의 사용자·비밀번호는 기록에 들어가지 않는다.
        "database": settings.database_url.rsplit("/", 1)[-1],
        "embedding_models": {lang: embedder(lang).identity for lang in languages},
        "vector_checks": vector_checks,
        "dataset": args.dataset.name,
        "order": args.order,
        "seed": args.seed if args.order == "shuffle" else None,
        "git_commit": git_commit(),
        "ollama_version": (state.get("version") or {}).get("version"),
        "ollama_ps_after": state.get("ps"),
        "model_digest": model_digest(state, model_in_use) if ollama else None,
        "think": settings.ollama_think if ollama else None,
        "language_guard": settings.language_guard if ollama else False,
        "records_path": display_path(gen_path),
    }
    write_json(meta_path(gen_path), gen_meta)

    # 모든 답이 만들어진 뒤에만 판정한다. 판정 모델이 생성 모델과 다르면, 둘을 번갈아 부를 때 Ollama가
    # 질문마다 모델을 바꿔 올리고 그 다시 올리는 시간이 생성 시간에 섞인다.
    # --skip-judge면 판정 없이 키워드 커버리지 등만으로 리포트를 만든다(빠르고 무료).
    judgments = judge_meta = None
    if not args.skip_judge:
        # --judge-num-ctx 0은 None으로 바뀌어 v10까지의 판정 호출(num_ctx·truncate 없음)을 그대로 보낸다.
        # 라벨을 주지 않으면 'legacy' 또는 'ctx8192' 같은 이름이 붙는다.
        num_ctx = args.judge_num_ctx or None
        config = JudgeConfig(
            model=judge_model, num_ctx=num_ctx, label=args.judge_label or default_label(num_ctx)
        )
        # 판정 모델의 토크나이저가 없으면 판정은 하되 잘림 확인은 못 한다는 것을 알린다.
        if use_counter and judge_counter is None:
            print(f"warning: no tokenizer mapped for {judge_model}; truncation is not checked")
        judgments, judge_meta = await judge_and_save(
            records,
            config,
            RUNS_DIR / f"{args.tag}.{config.label}.judge.jsonl",
            provider=settings.generation_provider,
            base_url=settings.ollama_base_url,
            api_key=settings.anthropic_api_key,
            count_tokens=judge_counter,
        )

    report = render_report(args.tag, gen_meta, records, judgments, judge_meta)
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    path = write_report(f"answer_eval_{args.tag}_{timestamp}.md", report)  # 출력하기 전에 먼저 저장
    print(report)
    print(f"\nwritten to {path}")
    # 판정 오류가 하나라도 있으면 리포트는 남기되 종료 코드 1로 알려, 자동 실행 스크립트가 알아챌 수 있게
    # 한다.
    errors = sum(1 for j in judgments or [] if j["error"])
    if errors:
        print(f"{errors} judge errors; see the report", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    # 명령행 옵션. 기본값은 앱 기본 동작(top-5, 설정의 검색 모드)과 v11 판정 설정(J1: num_ctx 8192)이다.
    # --seed 20261003은 v11 규칙에 적힌 seed다.
    parser = argparse.ArgumentParser()
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--tag", default="run")
    parser.add_argument("--skip-judge", action="store_true", help="판정 호출을 건너뛴다(빠르고 무료)")
    parser.add_argument("--mode", choices=["dense", "hybrid", "rerank"], default=None)
    parser.add_argument("--dataset", type=Path, default=DATASET_PATH)
    parser.add_argument(
        "--judge-model", default=None, help="판정 모델. 기본값은 지금 쓰는 생성 모델"
    )
    parser.add_argument(
        "--judge-num-ctx",
        type=int,
        default=DEFAULT_JUDGE_NUM_CTX,
        help="Ollama 판정 문맥 크기. 0이면 num_ctx 없이 v11 이전 호출을 보낸다",
    )
    parser.add_argument("--judge-label", default=None, help="판정 파일 이름에 붙는 라벨. 예: J1")
    parser.add_argument("--order", choices=["dataset", "shuffle"], default="dataset")
    parser.add_argument("--seed", type=int, default=20261003, help="--order shuffle에 쓰는 seed")
    parser.add_argument("--no-token-count", action="store_true", help="토크나이저로 토큰 수 세기를 건너뛴다")
    parser.add_argument(
        "--cross-lingual", action="store_true",
        help="한국어 질문이 한국어와 영어 청크를 함께 검색한다(docs/experiments.md v12)",
    )
    parser.add_argument(
        "--score-floor", type=float, default=None,
        help="dense 점수 바닥값. 기본값은 각 질문을 임베딩한 모델의 바닥값",
    )
    parser.add_argument(
        "--no-vector-check", action="store_true",
        help="저장된 벡터가 설정된 모델로 만든 것인지 확인하는 단계를 건너뛴다",
    )
    # 콘솔 코드 페이지에 답의 어떤 글자가 없더라도 오래 걸리는 실행이 그 때문에 끝나면 안 된다.
    sys.stdout.reconfigure(errors="backslashreplace")
    sys.exit(asyncio.run(main(parser.parse_args())))

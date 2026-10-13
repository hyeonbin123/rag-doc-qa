"""Retrieval-only evaluation: Hit@k, MRR and retrieval latency.

Usage:
    python -m eval.run_retrieval_eval [--top-k 10] [--tag v1_baseline]
        [--mode dense|hybrid|rerank] [--dataset eval/qa_dev.jsonl [more.jsonl ...]]
        [--lexical-weight 0.75] [--rerank-pool 10] [--reranker-model NAME]
        [--score-floor 0.3] [--cross-lingual] [--exact] [--no-vector-check]

Tune on the tuning sets (eval/qa_dev.jsonl, eval/qa_dev_ko.jsonl, eval/qa_dev2_ko.jsonl);
the other sets are held out for testing. In rerank mode the model and pool follow each
question's language; --reranker-model and --rerank-pool override them for every question.

A hit is a retrieved chunk from an expected page in any translation, so an English chunk
of an expected Korean page counts (the --cross-lingual search can return one). For a
one-language search this is the same as matching the path exactly.

Every run also writes per-question records (ranked chunk ids, paths and scores) to
eval/runs/<tag>.retrieval.jsonl; eval/retrieval_runs.py compares runs and score floors.
"""

# [파일 역할] 검색 단계만 평가하는 스크립트. 질문셋의 문항마다 앱과 같은 검색(retrieve)을 돌려 Hit@3/5/10,
# MRR, 검색 지연(p50/p95)을 내고, 리포트(eval/reports/)와 문항별 기록(eval/runs/<tag>.retrieval.jsonl)을
# 남긴다.
# [왜 필요한가] README '핵심 결과'의 v1~v13 검색 결정(청킹 정제, hybrid·rerank 채택 여부, 한국어 임베딩
# 교체)은 모두 이 스크립트의 수치로 내렸다. 답변 생성 없이 몇 분 안에 돌아가므로 파라미터 튜닝은 튜닝용 셋에서
# 이 스크립트로만 하고, 테스트셋에는 고른 설정 하나만 돌린다(docs/experiments.md '원칙').
# [흐름] main: 설정 → (rerank) 재정렬 모델 미리 올림 → 저장 벡터 확인 → (--exact) 정확 탐색으로 전환 → 실행
# 계획 기록 → 문항별 evaluate_question → aggregate → 리포트·기록·meta 저장.
# [연결] 검색 로직은 app/services/retrieval.py, 측정 전 확인은 eval/retrieval_checks.py, 기록 분석은
# eval/retrieval_runs.py. tests/test_retrieval_eval.py가 지표 함수와 교차언어 판정을 검증한다.

from __future__ import annotations

import argparse
import asyncio
import statistics
import time
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

# torch: 기록에 torch 스레드 수를 남기려고 가져온다. CPU 임베딩·재정렬 지연이 스레드 수에 따라 달라지므로 측정
# 조건으로 적는다.
import torch

# 앱의 설정·DB 세션·임베딩·언어 판별·재정렬·검색 함수를 그대로 써서 서비스와 같은 경로를 잰다.
# LEXICAL_WEIGHT·RERANK_POOLS는 옵션 기본값으로 쓴다.
# 평가 공용 모듈(eval.common)과 측정 전 확인(eval.retrieval_checks)도 가져온다.
from app.config import get_settings
from app.db.session import async_session_maker
from app.services.embedding import get_embedding_service
from app.services.language import Language, detect_language
from app.services.reranking import RerankerService, get_reranker_service
from app.services.retrieval import LEXICAL_WEIGHT, RERANK_POOLS, page_key, retrieve, score_floor_for
from eval.common import (
    DATASET_PATH,
    RUNS_DIR,
    EvalQuestion,
    git_commit,
    load_dataset,
    write_json,
    write_jsonl,
    write_report,
)
from eval.retrieval_checks import check_stored_vectors, dense_search_plan, force_exact_search

# 결과가 5개 미만인 문항을 'short'로 센다. 답변 파이프라인은 상위 5개를 생성기에 넘기므로, 바닥값이 결과를
# 잘라 5개 밑으로 내려가면 생성 컨텍스트가 줄어든다는 뜻이다.
SHORT = 5  # fewer results than this means the generator would get fewer than top 5


# 경로 목록을 페이지 키 목록으로 바꾼다. 번역이 달라도 같은 페이지면 같은 키가 된다.
def _pages(paths: list[str]) -> list[str]:
    return [page_key(p) for p in paths]


# 상위 k개 안에 정답 페이지가 하나라도 있으면 True. v12부터 페이지 단위로 비교하므로 정답 페이지의 다른
# 번역(영어 원문 청크)도 맞음으로 센다. 한 언어만 검색할 때는 경로를 그대로 비교한 이전 정의와 결과가 같다.
def hit_at_k(ranked_paths: list[str], expected: list[str], k: int) -> bool:
    expected_pages = set(_pages(expected))
    return any(p in expected_pages for p in _pages(ranked_paths[:k]))


# 처음 정답 페이지가 나온 순위의 역수(1위 1.0, 2위 0.5 ...). 결과 안에 없으면 0. 문항별 값을 평균하면 MRR이다.
def reciprocal_rank(ranked_paths: list[str], expected: list[str]) -> float:
    expected_pages = set(_pages(expected))
    for rank, page in enumerate(_pages(ranked_paths), start=1):
        if page in expected_pages:
            return 1.0 / rank
    return 0.0


# 언어를 받아 재정렬 모델을 돌려주는 함수를 만든다. 기본은 언어별 설정 모델(영어 MiniLM-L6, 한국어 다국어
# 모델, docs/experiments.md v9). --reranker-model을 주면 언어와 상관없이 모든 질문에 그 모델 하나를
# 쓴다(모델끼리 비교할 때).
def reranker_lookup(model_override: str | None) -> Callable[[Language], RerankerService]:
    if model_override is None:
        return get_reranker_service  # the configured model for each question's language
    fixed = RerankerService(model_override)
    return lambda language: fixed


# 이 언어 질문에 쓸 dense 점수 바닥값. --score-floor가 있으면 그 값(v12 바닥값 측정은 0으로 돌림), 없으면 그
# 언어 질문을 임베딩하는 모델의 값(앱과 같음).
def question_floor(args: argparse.Namespace, embedder, language: Language) -> float:
    """--score-floor if given, else the floor of the model that embeds this language."""
    if args.score_floor is not None:
        return args.score_floor
    return score_floor_for(embedder(language).model_name)


# 문항 하나를 검색하고 지표와 기록을 dict로 돌려준다. 기록에는 순위별 청크 id·경로·점수가 들어가,
# eval/retrieval_runs.py가 검색을 다시 돌리지 않고 바닥값을 바꿔 보거나 두 실행을 비교할 수 있다.
async def evaluate_question(
    db,
    embedder,
    q: EvalQuestion,
    args: argparse.Namespace,
    reranker_for: Callable[[Language], RerankerService] | None,
    dataset: str = "",
) -> dict:
    language = detect_language(q.question)
    query_vector = embedder(language).embed_query(q.question)
    reranker = reranker_for(language) if reranker_for else None
    floor = question_floor(args, embedder, language)
    cross_lingual = bool(args.cross_lingual) and language == "ko"
    # Timed after the embedding so every mode is measured on the same work: the DB
    # queries, plus the cross-encoder in rerank mode.
    start = time.perf_counter()
    retrieved = await retrieve(
        db,
        q.question,
        query_vector,
        args.top_k,
        args.mode,
        language=language,
        lexical_weight=args.lexical_weight,
        reranker=reranker,
        rerank_pool=args.rerank_pool,
        score_floor=floor,
        cross_lingual=cross_lingual,
    )
    latency_ms = (time.perf_counter() - start) * 1000
    # Hit와 MRR은 청크가 아니라 문서 경로(→ 페이지) 기준으로 센다. 같은 페이지의 청크가 여러 개 나와도 첫
    # 순위만 의미가 있다.
    ranked_paths = [r.source_path for r in retrieved]

    return {
        "id": q.id,
        "dataset": dataset,
        "question": q.question,
        "language": language,
        "expected_source_paths": q.expected_source_paths,
        "cross_lingual": cross_lingual,
        "score_floor": floor,
        "results": [
            {
                "rank": rank,
                "chunk_id": str(r.chunk_id),
                "source_path": r.source_path,
                "score": round(float(r.score), 6),
            }
            for rank, r in enumerate(retrieved, start=1)
        ],
        "n_results": len(retrieved),
        "hit@3": hit_at_k(ranked_paths, q.expected_source_paths, 3),
        "hit@5": hit_at_k(ranked_paths, q.expected_source_paths, 5),
        "hit@10": hit_at_k(ranked_paths, q.expected_source_paths, 10),
        "reciprocal_rank": reciprocal_rank(ranked_paths, q.expected_source_paths),
        "retrieved_paths": ranked_paths,
        "latency_ms": latency_ms,
    }


# 문항별 결과를 평균 지표로 모은다. p95는 statistics.quantiles(n=20)의 19개 경계값 중 마지막(95%)이다. 문항이
# 하나뿐이면 그 값을 그대로 쓴다.
def aggregate(results: list[dict]) -> dict:
    n = len(results)
    latencies = [r["latency_ms"] for r in results]
    return {
        "n": n,
        "hit@3": sum(r["hit@3"] for r in results) / n,
        "hit@5": sum(r["hit@5"] for r in results) / n,
        "hit@10": sum(r["hit@10"] for r in results) / n,
        "mrr": sum(r["reciprocal_rank"] for r in results) / n,
        "short": sum(r["n_results"] < SHORT for r in results),
        "p50": statistics.median(latencies),
        "p95": statistics.quantiles(latencies, n=20)[18] if n > 1 else latencies[0],
    }


# 리포트 표의 한 줄(셋 이름과 지표)을 만든다.
def _aggregate_row(label: str, agg: dict) -> str:
    return (
        f"| {label} | {agg['n']} | {agg['hit@3']:.2f} | {agg['hit@5']:.2f} | {agg['hit@10']:.2f} "
        f"| {agg['mrr']:.3f} | {agg['short']} | {agg['p50']:.0f} | {agg['p95']:.0f} |"
    )


# 평가 한 번을 실행한다. --mode를 주지 않으면 설정의 RETRIEVAL_MODE를 따른다. 교차언어 검색은 dense에만 구현돼
# 있어 다른 모드면 바로 멈춘다.
async def main(args: argparse.Namespace) -> None:
    settings = get_settings()
    args.mode = args.mode or settings.retrieval_mode
    if args.cross_lingual and args.mode != "dense":
        raise SystemExit("--cross-lingual is dense only")
    embedder = get_embedding_service  # per-language lookup, called with each question's language
    # --dataset에 여러 셋을 주면 함께 돌려 전체와 셋별 지표를 같이 낸다(v12 dev는 qa_dev_ko + qa_dev2_ko
    # 72문항을 한 번에 돌렸다).
    datasets = [(path, load_dataset(path)) for path in args.dataset]
    languages = sorted({detect_language(q.question) for _, qs in datasets for q in qs})

    reranker_for = None
    # 재정렬 모델을 처음 부를 때의 적재 시간이 첫 문항의 지연에 섞이지 않도록 언어마다 한 번씩 미리 호출해
    # 둔다(v6·v9의 지연 예산 1초 판단이 이 지연 값으로 내려졌다).
    if args.mode == "rerank":
        reranker_for = reranker_lookup(args.reranker_model)
        for language in languages:  # keep one-off setup cost out of the timings
            reranker_for(language).score("warm-up", ["warm-up"])

    started = datetime.now(UTC)
    results = []
    vector_checks = []
    async with async_session_maker() as db:
        if not args.no_vector_check:
            # The stored vectors of every searched language must come from the model that
            # embeds the questions searching them (a cross-lingual Korean question searches
            # the English chunks with the Korean model).
            for language in languages:
                vector_checks.append(await check_stored_vectors(db, embedder(language), language))
            if args.cross_lingual and "ko" in languages:
                vector_checks.append(await check_stored_vectors(db, embedder("ko"), "en"))
        # --exact면 이 세션의 인덱스 스캔을 꺼 정확 탐색으로 잰다. 계획대로 돈 실행과 상위 10개가 같은지
        # 비교하는 기준이다.
        if args.exact:
            await force_exact_search(db)
        # 실제로 검색하는 언어(교차언어면 영어 포함)마다 dense 검색의 실행 계획을 기록한다. HNSW 인덱스를
        # 썼는지 Seq Scan(정확 탐색)이었는지를 리포트에서 알 수 있다.
        searched = set(languages) | ({"en"} if args.cross_lingual and "ko" in languages else set())
        plans = {lang: await dense_search_plan(db, lang, args.top_k) for lang in sorted(searched)}
        for path, questions in datasets:
            for q in questions:
                results.append(await evaluate_question(db, embedder, q, args, reranker_for, path.name))

    # 리포트 머리에는 결과를 해석하는 데 필요한 조건(모델, DB 이름, 검색 모드, 정확/계획대로, 실행 계획,
    # 바닥값, 벡터 확인, BM25 가중치, 재정렬 모델과 후보 수)을 모두 적는다.
    agg = aggregate(results)
    floors = {lang: question_floor(args, embedder, lang) for lang in languages}
    lines = [
        f"# Retrieval eval report ({args.tag})",
        "",
        f"- date: {started.isoformat()}",
        f"- embedding models: en {settings.embedding_model_name}, ko {settings.embedding_model_name_ko}",
        f"- database: {settings.database_url.rsplit('/', 1)[-1]}",
        f"- top_k: {args.top_k}",
        f"- retrieval mode: {args.mode}"
        + (" (Korean questions search the Korean and English chunks, one translation per page)"
           if args.cross_lingual else ""),
        f"- search: {'exact (index scans off)' if args.exact else 'as planned'}; dense plan: "
        + "; ".join(f"{lang} {' > '.join(nodes)}" for lang, nodes in plans.items()),
        f"- score floor: {', '.join(f'{lang} {floor}' for lang, floor in floors.items())}"
        + (" (dense only)" if args.mode != "dense" else ""),
    ]
    if vector_checks:
        lines.append(
            "- stored vectors checked: "
            + ", ".join(
                f"{c['language']} chunks vs {c['model']} (min cosine {c['min_cosine']})"
                for c in vector_checks
            )
        )
    if args.mode == "hybrid":
        lines.append(f"- lexical: BM25, RRF weight {args.lexical_weight}")
    if args.mode == "rerank":
        for language in languages:
            model = args.reranker_model or settings.reranker_model_for(language)
            pool = args.rerank_pool or RERANK_POOLS[language]
            lines.append(f"- reranker ({language}): {model}, top {pool} of each of dense and BM25")
    lines += [
        f"- dataset: {', '.join(path.name for path, _ in datasets)}",
        f"- questions: {agg['n']}",
        "- hit: a chunk of an expected page, in any translation",
        f"- short: questions with fewer than {SHORT} results (the score floor cut the rest)",
        "- latency: retrieval only (after the query embedding), this machine's CPU",
        "",
        "## Aggregate metrics",
        "",
        "| set | questions | Hit@3 | Hit@5 | Hit@10 | MRR | short | latency p50 (ms) | latency p95 (ms) |",
        "|---|---|---|---|---|---|---|---|---|",
        _aggregate_row("all", agg),
    ]
    if len(datasets) > 1:
        for path, _ in datasets:
            subset = [r for r in results if r["dataset"] == path.name]
            lines.append(_aggregate_row(path.name, aggregate(subset)))
    lines += [
        "",
        "## Per-question",
        "",
        "| id | hit@3 | hit@5 | hit@10 | RR | results | ms | question |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in results:
        lines.append(
            f"| {r['id']} | {r['hit@3']} | {r['hit@5']} | {r['hit@10']} "
            f"| {r['reciprocal_rank']:.2f} | {r['n_results']} | {r['latency_ms']:.0f} | {r['question']} |"
        )

    report = "\n".join(lines)
    print(report)

    # 문항별 기록에서는 retrieved_paths를 뺀다(results에 같은 경로가 이미 있다). meta에는 실행 조건과 전체
    # 지표를 남긴다.
    records_path = write_jsonl(
        RUNS_DIR / f"{args.tag}.retrieval.jsonl",
        [{k: v for k, v in r.items() if k != "retrieved_paths"} for r in results],
    )
    write_json(
        RUNS_DIR / f"{args.tag}.retrieval.meta.json",
        {
            "date": started.isoformat(),
            "tag": args.tag,
            "git_commit": git_commit(),
            "database": settings.database_url.rsplit("/", 1)[-1],
            "embedding_models": {lang: embedder(lang).identity for lang in languages},
            "mode": args.mode,
            "top_k": args.top_k,
            "score_floors": floors,
            "cross_lingual": bool(args.cross_lingual),
            "exact": bool(args.exact),
            "dense_plans": plans,
            "datasets": [path.name for path, _ in datasets],
            "vector_checks": vector_checks,
            "torch_threads": torch.get_num_threads(),
            "aggregate": agg,
        },
    )
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    path = write_report(f"retrieval_eval_{args.tag}_{timestamp}.md", report)
    print(f"\nwritten to {path} and {records_path}")


if __name__ == "__main__":
    # 명령행 옵션. --top-k 기본 10(Hit@10까지 재려고), --lexical-weight 기본은 v5에서 qa_dev로 고른 0.75,
    # --rerank-pool·--reranker-model을 주지 않으면 언어별 설정값을 쓴다.
    parser = argparse.ArgumentParser()
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--tag", default="run")
    parser.add_argument("--mode", choices=["dense", "hybrid", "rerank"], default=None)
    parser.add_argument("--dataset", type=Path, nargs="+", default=[DATASET_PATH])
    parser.add_argument("--lexical-weight", type=float, default=LEXICAL_WEIGHT)
    parser.add_argument(
        "--rerank-pool", type=int, default=None, help="defaults to RERANK_POOLS[language]"
    )
    parser.add_argument(
        "--reranker-model", default=None, help="defaults to the language's RERANKER_MODEL_NAME"
    )
    parser.add_argument(
        "--score-floor", type=float, default=None,
        help="dense score floor for every question; defaults to each model's (SCORE_FLOORS)",
    )
    parser.add_argument(
        "--cross-lingual", action="store_true",
        help="Korean questions search the Korean and English chunks (needs a database whose "
        "English chunks were embedded by the Korean model)",
    )
    parser.add_argument("--exact", action="store_true", help="exact search instead of HNSW")
    parser.add_argument(
        "--no-vector-check", action="store_true",
        help="skip checking that the stored vectors come from the configured models",
    )
    asyncio.run(main(parser.parse_args()))

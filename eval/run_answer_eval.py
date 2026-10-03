"""Full-pipeline answer evaluation: keyword coverage + LLM-as-judge faithfulness and
correctness.

Every answer is generated first and stored per item in eval/runs/<tag>.gen.jsonl (the
ranked passages with chunk ids and contents, the answer, timings and token counts). The
judge then scores the stored answers and its replies go to
eval/runs/<tag>.<judge label>.judge.jsonl, with the prompt's token count as Ollama read
it and as the model's tokenizer counts it, so a cut prompt is visible per item.
eval/run_judge.py reruns a judge on stored answers.

The judge runs on whichever provider GENERATION_PROVIDER selects, so a fully local
(free) eval run is possible. --judge-model pins the judge to one model, so runs that
compare generation models are all scored by the same judge. The Ollama judge asks for an
8192-token context with truncate=false (docs/experiments.md v11); --judge-num-ctx 0
sends the pre-v11 call, which ran in Ollama's default context.

Usage:
    python -m eval.run_answer_eval [--top-k 5] [--tag v1_baseline] [--mode dense|hybrid|rerank] [--skip-judge]
        [--dataset eval/qa_test2.jsonl] [--judge-model qwen2.5:7b-instruct]
        [--judge-num-ctx 8192] [--judge-label J1] [--order dataset|shuffle] [--seed 20261003]
        [--no-token-count]
"""

from __future__ import annotations

import argparse
import asyncio
import random
import re
import subprocess
import sys
import time
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

from app.config import get_settings
from app.db.session import async_session_maker
from app.services.embedding import get_embedding_service
from app.services.generation import (
    OLLAMA_ANSWER_PROMPT,
    _build_user_message,
    get_generation_service,
    system_prompt_for,
)
from app.services.language import Language, detect_language
from app.services.reranking import RerankerService, get_reranker_service
from app.services.retrieval import RetrievalMode, RetrievedChunk, retrieve
from eval.answer_report import display_path, render_report
from eval.common import (
    DATASET_PATH,
    RUNS_DIR,
    EvalQuestion,
    load_dataset,
    write_json,
    write_jsonl,
    write_report,
)
from eval.judge import DEFAULT_JUDGE_NUM_CTX, JUDGE_SCHEMA, JUDGE_TOOL, JudgeConfig, TokenCounter
from eval.run_judge import default_label, judge_and_save, meta_path, ollama_state
from eval.tokens import counter_for_model

__all__ = ["JUDGE_SCHEMA", "JUDGE_TOOL", "generate_answer", "generation_order", "keyword_coverage"]

# Kana (U+3040-U+30FF) and Han (U+4E00-U+9FFF) characters. The docs never use them, so
# in an answer they mean the model slipped into Japanese or Chinese (seen in Korean
# answers from the 7B model).
KANA_HAN_RE = re.compile(r"[぀-ヿ一-鿿]")

GenerationPromptCounter = Callable[[str, list[RetrievedChunk], Language], int]


def keyword_coverage(answer: str, keywords: list[str]) -> float:
    if not keywords:
        return 1.0
    lower_answer = answer.lower()
    hits = sum(1 for kw in keywords if kw.lower() in lower_answer)
    return hits / len(keywords)


def generation_order(n: int, order: str, seed: int) -> list[int]:
    """Indices in the order to generate: the dataset's, or a shuffle fixed by the seed."""
    indices = list(range(n))
    if order == "shuffle":
        random.Random(seed).shuffle(indices)
    return indices


def ollama_answer_prompt_counter(count_tokens: TokenCounter) -> GenerationPromptCounter:
    """Counts the Ollama answer call's prompt (system rules + passages + question)."""

    def count(question: str, chunks: list[RetrievedChunk], language: Language) -> int:
        return count_tokens(
            [
                {"role": "system", "content": system_prompt_for(OLLAMA_ANSWER_PROMPT, language)},
                {"role": "user", "content": _build_user_message(question, chunks)},
            ]
        )

    return count


async def generate_answer(
    db,
    embedder,
    generator,
    q: EvalQuestion,
    top_k: int,
    mode: RetrievalMode,
    reranker: RerankerService | None,
    count_generation_prompt: GenerationPromptCounter | None = None,
) -> dict:
    language = detect_language(q.question)
    query_vector = embedder(language).embed_query(q.question)
    retrieved = await retrieve(
        db, q.question, query_vector, top_k, mode, language=language, reranker=reranker
    )
    start = time.perf_counter()
    generation_result = await generator.answer(q.question, retrieved, language=language)
    generation_ms = (time.perf_counter() - start) * 1000

    paths = [r.source_path for r in retrieved]
    first_hit_rank = next(
        (rank for rank, path in enumerate(paths, start=1) if path in q.expected_source_paths), None
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
        "answer": generation_result.answer,
        "cited_chunk_numbers": generation_result.cited_chunk_numbers,
        "generation_ms": generation_ms,
        # Both Ollama calls (answer + citations) summed, as Ollama reported them.
        "generation_input_tokens": generation_result.input_tokens,
        "generation_output_tokens": generation_result.output_tokens,
        # The answer call's prompt by the tokenizer: above 8191 it would have been cut.
        "generation_prompt_tokens_counted": (
            count_generation_prompt(q.question, retrieved, language) if count_generation_prompt else None
        ),
        "keyword_coverage": keyword_coverage(generation_result.answer, q.must_include_keywords),
        "kana_han": bool(KANA_HAN_RE.search(generation_result.answer)),
    }


def git_commit() -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True, timeout=10
        )
        return result.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None


async def main(args: argparse.Namespace) -> int:
    settings = get_settings()
    mode = args.mode or settings.retrieval_mode
    embedder = get_embedding_service  # per-language lookup, called with each question's language
    generator = get_generation_service()
    questions = load_dataset(args.dataset)
    ollama = settings.generation_provider == "ollama"
    model_in_use = settings.ollama_model_name if ollama else settings.claude_model_name
    judge_model = args.judge_model or model_in_use
    use_counter = ollama and not args.no_token_count
    gen_counter = counter_for_model(model_in_use) if use_counter else None
    judge_counter = counter_for_model(judge_model) if use_counter and not args.skip_judge else None

    started = datetime.now(UTC).isoformat()
    records: list[dict] = [{} for _ in questions]
    async with async_session_maker() as db:
        for order_index, index in enumerate(generation_order(len(questions), args.order, args.seed)):
            q = questions[index]
            reranker = None
            if mode == "rerank":  # like the embedder, chosen by the question's language
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
        "dataset": args.dataset.name,
        "order": args.order,
        "seed": args.seed if args.order == "shuffle" else None,
        "git_commit": git_commit(),
        "ollama_version": (state.get("version") or {}).get("version"),
        "ollama_ps_after": state.get("ps"),
        "records_path": display_path(gen_path),
    }
    write_json(meta_path(gen_path), gen_meta)

    # Judge only after every answer exists. With a judge model other than the generator,
    # interleaving the two would make Ollama swap models on every question, and the
    # reload time would land in the generation timings.
    judgments = judge_meta = None
    if not args.skip_judge:
        num_ctx = args.judge_num_ctx or None
        config = JudgeConfig(
            model=judge_model, num_ctx=num_ctx, label=args.judge_label or default_label(num_ctx)
        )
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
    path = write_report(f"answer_eval_{args.tag}_{timestamp}.md", report)  # before printing
    print(report)
    print(f"\nwritten to {path}")
    errors = sum(1 for j in judgments or [] if j["error"])
    if errors:
        print(f"{errors} judge errors; see the report", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--tag", default="run")
    parser.add_argument("--skip-judge", action="store_true", help="skip the judge calls (fast, free)")
    parser.add_argument("--mode", choices=["dense", "hybrid", "rerank"], default=None)
    parser.add_argument("--dataset", type=Path, default=DATASET_PATH)
    parser.add_argument(
        "--judge-model", default=None, help="defaults to the generation model in use"
    )
    parser.add_argument(
        "--judge-num-ctx",
        type=int,
        default=DEFAULT_JUDGE_NUM_CTX,
        help="Ollama judge context; 0 sends the pre-v11 call without num_ctx",
    )
    parser.add_argument("--judge-label", default=None, help="names the judgment file, e.g. J1")
    parser.add_argument("--order", choices=["dataset", "shuffle"], default="dataset")
    parser.add_argument("--seed", type=int, default=20261003, help="for --order shuffle")
    parser.add_argument("--no-token-count", action="store_true", help="skip the tokenizer counts")
    # A console code page that lacks some character in an answer must not end a long run.
    sys.stdout.reconfigure(errors="backslashreplace")
    sys.exit(asyncio.run(main(parser.parse_args())))

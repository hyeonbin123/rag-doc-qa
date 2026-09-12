"""Full-pipeline answer evaluation: keyword coverage + LLM-as-judge
faithfulness and correctness, against eval/qa_dataset.jsonl.

The judge runs on whichever provider GENERATION_PROVIDER selects, so a fully
local (free) eval run is possible. --judge-model pins the judge to one model, so
runs that compare generation models are all scored by the same judge.

Usage:
    python -m eval.run_answer_eval [--top-k 5] [--tag v1_baseline] [--mode dense|hybrid|rerank] [--skip-judge]
                                   [--dataset eval/qa_test2.jsonl] [--judge-model qwen2.5:7b-instruct]
"""

from __future__ import annotations

import argparse
import asyncio
import json
import re
import statistics
import time
from datetime import UTC, datetime
from pathlib import Path

import httpx
from anthropic import AsyncAnthropic

from app.config import get_settings
from app.db.session import async_session_maker
from app.services.embedding import get_embedding_service
from app.services.generation import get_generation_service
from app.services.language import detect_language
from app.services.reranking import RerankerService, get_reranker_service
from app.services.retrieval import RetrievalMode, retrieve
from eval.common import DATASET_PATH, EvalQuestion, load_dataset, write_report

# Kana (U+3040-U+30FF) and Han (U+4E00-U+9FFF) characters. The docs never use them, so
# in an answer they mean the model slipped into Japanese or Chinese (seen in Korean
# answers from the 7B model).
KANA_HAN_RE = re.compile(r"[぀-ヿ一-鿿]")

JUDGE_SCHEMA = {
    "type": "object",
    "properties": {
        "faithfulness_score": {
            "type": "integer",
            "minimum": 1,
            "maximum": 5,
            "description": "1-5, is the answer supported by the given context?",
        },
        "hallucinated": {
            "type": "boolean",
            "description": "true if the answer states something not supported by context",
        },
        "correctness_score": {
            "type": "integer",
            "minimum": 1,
            "maximum": 5,
            "description": "1-5, how well does the answer match the reference answer?",
        },
    },
    "required": ["faithfulness_score", "hallucinated", "correctness_score"],
}

JUDGE_TOOL = {
    "name": "score_answer",
    "description": "Score a generated answer for faithfulness/groundedness and correctness.",
    "input_schema": JUDGE_SCHEMA,
}


def keyword_coverage(answer: str, keywords: list[str]) -> float:
    if not keywords:
        return 1.0
    lower_answer = answer.lower()
    hits = sum(1 for kw in keywords if kw.lower() in lower_answer)
    return hits / len(keywords)


def _build_judge_prompt(question: str, context: str, answer: str, reference: str) -> str:
    return (
        f"Question: {question}\n\n"
        f"Context passages the model was given:\n{context}\n\n"
        f"Model's answer:\n{answer}\n\n"
        f"Reference answer:\n{reference}\n\n"
        "Score the model's answer. Both scores use a 1-5 scale, where 1 is worst and 5 is best."
    )


async def judge_with_anthropic(settings, prompt: str, model: str) -> dict:
    client = AsyncAnthropic(api_key=settings.anthropic_api_key)
    response = await client.messages.create(
        model=model,
        max_tokens=256,
        tools=[JUDGE_TOOL],
        tool_choice={"type": "tool", "name": "score_answer"},
        messages=[{"role": "user", "content": prompt}],
    )
    tool_use = next(b for b in response.content if b.type == "tool_use")
    return tool_use.input


async def judge_with_ollama(settings, prompt: str, model: str) -> dict:
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "format": JUDGE_SCHEMA,
        "stream": False,
        "options": {"temperature": 0},
    }
    async with httpx.AsyncClient(timeout=180.0) as client:
        response = await client.post(f"{settings.ollama_base_url.rstrip('/')}/api/chat", json=payload)
        response.raise_for_status()
        data = response.json()
    return json.loads(data["message"]["content"])


async def judge_answer(
    settings, question: str, context: str, answer: str, reference: str, judge_model: str
) -> dict:
    prompt = _build_judge_prompt(question, context, answer, reference)
    if settings.generation_provider == "ollama":
        result = await judge_with_ollama(settings, prompt, judge_model)
    else:
        result = await judge_with_anthropic(settings, prompt, judge_model)

    # An out-of-range score would silently skew every average, so fail loudly instead.
    for key in ("faithfulness_score", "correctness_score"):
        if not 1 <= result[key] <= 5:
            raise ValueError(f"judge returned {key}={result[key]}, outside the 1-5 scale")
    return result


async def generate_answer(
    db,
    embedder,
    generator,
    q: EvalQuestion,
    top_k: int,
    mode: RetrievalMode,
    reranker: RerankerService | None,
) -> dict:
    language = detect_language(q.question)
    query_vector = embedder(language).embed_query(q.question)
    retrieved = await retrieve(
        db, q.question, query_vector, top_k, mode, language=language, reranker=reranker
    )
    start = time.perf_counter()
    generation_result = await generator.answer(q.question, retrieved, language=language)
    generation_ms = (time.perf_counter() - start) * 1000

    return {
        "id": q.id,
        "question": q.question,
        "answer": generation_result.answer,
        "keyword_coverage": keyword_coverage(generation_result.answer, q.must_include_keywords),
        "generation_ms": generation_ms,
        "kana_han": bool(KANA_HAN_RE.search(generation_result.answer)),
        "context": "\n\n".join(r.content for r in retrieved),
    }


async def main(
    top_k: int,
    tag: str,
    mode: RetrievalMode | None,
    skip_judge: bool,
    dataset: Path,
    judge_model: str | None,
) -> None:
    settings = get_settings()
    mode = mode or settings.retrieval_mode
    embedder = get_embedding_service  # per-language lookup, called with each question's language
    generator = get_generation_service()
    questions = load_dataset(dataset)
    model_in_use = (
        settings.ollama_model_name
        if settings.generation_provider == "ollama"
        else settings.claude_model_name
    )
    judge_model = judge_model or model_in_use

    results = []
    async with async_session_maker() as db:
        for q in questions:
            reranker = None
            if mode == "rerank":  # like the embedder, chosen by the question's language
                reranker = get_reranker_service(detect_language(q.question))
            results.append(
                await generate_answer(db, embedder, generator, q, top_k, mode, reranker)
            )

    # Judge only after every answer exists. With a judge model other than the generator,
    # interleaving the two would make Ollama swap models on every question, and the
    # reload time would land in the generation timings.
    for q, r in zip(questions, results, strict=True):
        context = r.pop("context")
        judge_result = {"faithfulness_score": None, "hallucinated": None, "correctness_score": None}
        if not skip_judge and context:
            judge_result = await judge_answer(
                settings, q.question, context, r["answer"], q.reference_answer, judge_model
            )
        r.update(judge_result)

    n = len(results)
    avg_coverage = sum(r["keyword_coverage"] for r in results) / n
    scored = [r for r in results if r["faithfulness_score"] is not None]
    avg_faithfulness = sum(r["faithfulness_score"] for r in scored) / len(scored) if scored else None
    avg_correctness = sum(r["correctness_score"] for r in scored) / len(scored) if scored else None
    hallucinated_count = sum(1 for r in scored if r["hallucinated"])
    generation_p50 = statistics.median(r["generation_ms"] for r in results)
    kana_han_count = sum(1 for r in results if r["kana_han"])

    faithfulness_str = "n/a" if avg_faithfulness is None else f"{avg_faithfulness:.2f}"
    correctness_str = "n/a" if avg_correctness is None else f"{avg_correctness:.2f}"
    metrics_row = (
        f"| {avg_coverage:.2f} | {faithfulness_str} | {correctness_str} "
        f"| {hallucinated_count}/{len(scored)} | {generation_p50:.0f} | {kana_han_count}/{n} |"
    )

    lines = [
        f"# Answer eval report ({tag})",
        "",
        f"- date: {datetime.now(UTC).isoformat()}",
        f"- provider: {settings.generation_provider}",
        f"- model: {model_in_use}",
        f"- judge model: {judge_model}",
        f"- top_k: {top_k}",
        f"- retrieval mode: {mode}",
        f"- dataset: {dataset.name}",
        f"- questions: {n}",
        f"- judge skipped: {skip_judge}",
        "- generation time: both generation calls (answer + citations), this machine's GPU",
        "",
        "## Aggregate metrics",
        "",
        "| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Hallucinated "
        "| Generation p50 (ms) | Answers with kana/han |",
        "|---|---|---|---|---|---|",
        metrics_row,
        "",
        "## Per-question",
        "",
        "| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han |",
        "|---|---|---|---|---|---|---|",
        *(
            f"| {r['id']} | {r['keyword_coverage']:.2f} | {r['faithfulness_score']} "
            f"| {r['correctness_score']} | {r['hallucinated']} | {r['generation_ms']:.0f} "
            f"| {r['kana_han']} |"
            for r in results
        ),
        "",
        "## Worst questions (lowest keyword coverage)",
        "",
    ]
    worst = sorted(results, key=lambda r: r["keyword_coverage"])[:5]
    for r in worst:
        lines.append(f"- **{r['id']}** ({r['keyword_coverage']:.2f}): {r['question']}")
        lines.append(f"  > {r['answer'][:200]}")

    report = "\n".join(lines)
    print(report)

    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    path = write_report(f"answer_eval_{tag}_{timestamp}.md", report)
    print(f"\nwritten to {path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--tag", default="run")
    parser.add_argument("--skip-judge", action="store_true", help="skip Claude-as-judge calls (fast, free)")
    parser.add_argument("--mode", choices=["dense", "hybrid", "rerank"], default=None)
    parser.add_argument("--dataset", type=Path, default=DATASET_PATH)
    parser.add_argument(
        "--judge-model", default=None, help="defaults to the generation model in use"
    )
    args = parser.parse_args()
    asyncio.run(
        main(args.top_k, args.tag, args.mode, args.skip_judge, args.dataset, args.judge_model)
    )

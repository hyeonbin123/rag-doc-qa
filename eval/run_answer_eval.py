"""Full-pipeline answer evaluation: keyword coverage + LLM-as-judge
faithfulness and correctness, against eval/qa_dataset.jsonl.

The judge runs on whichever provider GENERATION_PROVIDER selects, so a fully
local (free) eval run is possible.

Usage:
    python -m eval.run_answer_eval [--top-k 5] [--tag v1_baseline] [--mode dense|hybrid] [--skip-judge]
"""

from __future__ import annotations

import argparse
import asyncio
import json
from datetime import UTC, datetime

import httpx
from anthropic import AsyncAnthropic

from app.config import get_settings
from app.db.session import async_session_maker
from app.services.embedding import get_embedding_service
from app.services.generation import get_generation_service
from app.services.retrieval import RetrievalMode, retrieve
from eval.common import EvalQuestion, load_dataset, write_report

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


async def judge_with_anthropic(settings, prompt: str) -> dict:
    client = AsyncAnthropic(api_key=settings.anthropic_api_key)
    response = await client.messages.create(
        model=settings.claude_model_name,
        max_tokens=256,
        tools=[JUDGE_TOOL],
        tool_choice={"type": "tool", "name": "score_answer"},
        messages=[{"role": "user", "content": prompt}],
    )
    tool_use = next(b for b in response.content if b.type == "tool_use")
    return tool_use.input


async def judge_with_ollama(settings, prompt: str) -> dict:
    payload = {
        "model": settings.ollama_model_name,
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


async def judge_answer(settings, question: str, context: str, answer: str, reference: str) -> dict:
    prompt = _build_judge_prompt(question, context, answer, reference)
    if settings.generation_provider == "ollama":
        result = await judge_with_ollama(settings, prompt)
    else:
        result = await judge_with_anthropic(settings, prompt)

    # An out-of-range score would silently skew every average, so fail loudly instead.
    for key in ("faithfulness_score", "correctness_score"):
        if not 1 <= result[key] <= 5:
            raise ValueError(f"judge returned {key}={result[key]}, outside the 1-5 scale")
    return result


async def evaluate_question(
    db,
    embedder,
    generator,
    settings,
    q: EvalQuestion,
    top_k: int,
    mode: RetrievalMode,
    skip_judge: bool,
) -> dict:
    query_vector = embedder.embed_query(q.question)
    retrieved = await retrieve(db, q.question, query_vector, top_k, mode)
    generation_result = await generator.answer(q.question, retrieved)

    coverage = keyword_coverage(generation_result.answer, q.must_include_keywords)

    judge_result = {"faithfulness_score": None, "hallucinated": None, "correctness_score": None}
    if not skip_judge and retrieved:
        context = "\n\n".join(r.content for r in retrieved)
        judge_result = await judge_answer(
            settings, q.question, context, generation_result.answer, q.reference_answer
        )

    return {
        "id": q.id,
        "question": q.question,
        "answer": generation_result.answer,
        "keyword_coverage": coverage,
        **judge_result,
    }


async def main(top_k: int, tag: str, mode: RetrievalMode | None, skip_judge: bool) -> None:
    settings = get_settings()
    mode = mode or settings.retrieval_mode
    embedder = get_embedding_service()
    generator = get_generation_service()
    questions = load_dataset()

    results = []
    async with async_session_maker() as db:
        for q in questions:
            results.append(
                await evaluate_question(db, embedder, generator, settings, q, top_k, mode, skip_judge)
            )

    n = len(results)
    avg_coverage = sum(r["keyword_coverage"] for r in results) / n
    scored = [r for r in results if r["faithfulness_score"] is not None]
    avg_faithfulness = sum(r["faithfulness_score"] for r in scored) / len(scored) if scored else None
    avg_correctness = sum(r["correctness_score"] for r in scored) / len(scored) if scored else None
    hallucinated_count = sum(1 for r in scored if r["hallucinated"])

    faithfulness_str = "n/a" if avg_faithfulness is None else f"{avg_faithfulness:.2f}"
    correctness_str = "n/a" if avg_correctness is None else f"{avg_correctness:.2f}"
    metrics_row = (
        f"| {avg_coverage:.2f} | {faithfulness_str} | {correctness_str} "
        f"| {hallucinated_count}/{len(scored)} |"
    )

    model_in_use = (
        settings.ollama_model_name
        if settings.generation_provider == "ollama"
        else settings.claude_model_name
    )

    lines = [
        f"# Answer eval report ({tag})",
        "",
        f"- date: {datetime.now(UTC).isoformat()}",
        f"- provider: {settings.generation_provider}",
        f"- model: {model_in_use}",
        f"- top_k: {top_k}",
        f"- retrieval mode: {mode}",
        f"- questions: {n}",
        f"- judge skipped: {skip_judge}",
        "",
        "## Aggregate metrics",
        "",
        "| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Hallucinated |",
        "|---|---|---|---|",
        metrics_row,
        "",
        "## Per-question",
        "",
        "| id | coverage | faithfulness | correctness | hallucinated |",
        "|---|---|---|---|---|",
        *(
            f"| {r['id']} | {r['keyword_coverage']:.2f} | {r['faithfulness_score']} "
            f"| {r['correctness_score']} | {r['hallucinated']} |"
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
    parser.add_argument("--mode", choices=["dense", "hybrid"], default=None)
    args = parser.parse_args()
    asyncio.run(main(args.top_k, args.tag, args.mode, args.skip_judge))

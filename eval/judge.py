"""LLM-as-judge for the answer eval.

The judge reads the question, the retrieved passages, the model's answer and the
reference answer, and returns faithfulness and correctness scores (1-5) and a
hallucination flag.

Until v10 the Ollama judge call set only temperature 0, so it ran in Ollama's default
context: 4096 tokens on this machine's 11 GB GPU (Ollama 0.35 picks the default by
VRAM). A judge prompt carries five passages, an answer of up to 1024 tokens and the
reference answer, and Ollama cuts an over-long prompt with only a server-log warning:
0.35.1 keeps the first 4 tokens and roughly the last half of the window, so the question
and the first passages are what disappear. The v11 judge (docs/experiments.md) asks for
8192 tokens with truncate=false, checks before the first call that every prompt fits, and
keeps Ollama's prompt_eval_count next to a tokenizer count of the same prompt, so a cut
prompt shows up in the per-item record. The old call stays available as the "legacy"
judge (num_ctx=None) to measure how often it was cut.
"""

from __future__ import annotations

import hashlib
import json
import time
from collections.abc import Awaitable, Callable
from dataclasses import asdict, dataclass

import httpx
from anthropic import AsyncAnthropic

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

DEFAULT_JUDGE_NUM_CTX = 8192
# Context left for the judge's reply, a JSON object of about 40 tokens.
REPLY_RESERVE_TOKENS = 256
# prompt_eval_count and a tokenizer count of the same prompt agree to a few tokens; a cut
# prompt comes back about half a window short.
TRUNCATION_TOLERANCE = 16

JudgeCall = Callable[[str], Awaitable["JudgeOutcome"]]
TokenCounter = Callable[[list[dict]], int]


@dataclass(frozen=True)
class JudgeConfig:
    model: str
    # None sends no num_ctx and no truncate flag: the pre-v11 call (Ollama's default
    # context, over-long prompts cut silently).
    num_ctx: int | None = DEFAULT_JUDGE_NUM_CTX
    label: str = "J1"

    @property
    def legacy(self) -> bool:
        return self.num_ctx is None


@dataclass
class JudgeOutcome:
    faithfulness_score: int | None = None
    hallucinated: bool | None = None
    correctness_score: int | None = None
    raw: str | None = None
    prompt_eval_count: int | None = None
    eval_count: int | None = None
    done_reason: str | None = None
    judge_ms: float | None = None
    error: str | None = None


class JudgeContextError(RuntimeError):
    """Some judge prompts do not fit in the configured context; nothing was sent."""


def build_judge_prompt(question: str, context: str, answer: str, reference: str) -> str:
    return (
        f"Question: {question}\n\n"
        f"Context passages the model was given:\n{context}\n\n"
        f"Model's answer:\n{answer}\n\n"
        f"Reference answer:\n{reference}\n\n"
        "Score the model's answer. Both scores use a 1-5 scale, where 1 is worst and 5 is best."
    )


def judge_messages(prompt: str) -> list[dict]:
    return [{"role": "user", "content": prompt}]


def judge_context(record: dict) -> str:
    """The passages as the judge has always seen them: contents only, in rank order."""
    return "\n\n".join(chunk["content"] for chunk in record["chunks"])


def ollama_judge_payload(prompt: str, config: JudgeConfig) -> dict:
    payload = {
        "model": config.model,
        "messages": judge_messages(prompt),
        "format": JUDGE_SCHEMA,
        "stream": False,
        "options": {"temperature": 0},
    }
    if not config.legacy:
        payload["options"]["num_ctx"] = config.num_ctx
        # Without this, Ollama cuts an over-long prompt and answers anyway.
        payload["truncate"] = False
    return payload


def validate_scores(result: dict) -> None:
    # An out-of-range score would silently skew every average, so fail loudly instead.
    for key in ("faithfulness_score", "correctness_score"):
        if not 1 <= result[key] <= 5:
            raise ValueError(f"judge returned {key}={result[key]}, outside the 1-5 scale")


def is_context_error(message: str) -> bool:
    message = message.lower()
    return any(
        phrase in message
        for phrase in ("context length", "context size", "available context", "longer than the context")
    )


def _error_message(response: httpx.Response) -> str:
    try:
        return str(response.json().get("error", response.text))
    except ValueError:
        return response.text


async def judge_with_ollama(
    base_url: str, prompt: str, config: JudgeConfig, timeout: float = 180.0
) -> JudgeOutcome:
    start = time.perf_counter()
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(
            f"{base_url.rstrip('/')}/api/chat", json=ollama_judge_payload(prompt, config)
        )
    elapsed_ms = (time.perf_counter() - start) * 1000
    if response.status_code >= 400:
        message = _error_message(response)
        if is_context_error(message):
            # Kept as a per-item error so a run can count them; scores stay empty.
            return JudgeOutcome(judge_ms=elapsed_ms, error=f"HTTP {response.status_code}: {message}")
        response.raise_for_status()

    data = response.json()
    raw = data["message"]["content"]
    result = json.loads(raw)
    validate_scores(result)
    return JudgeOutcome(
        faithfulness_score=result["faithfulness_score"],
        hallucinated=result["hallucinated"],
        correctness_score=result["correctness_score"],
        raw=raw,
        prompt_eval_count=data.get("prompt_eval_count"),
        eval_count=data.get("eval_count"),
        done_reason=data.get("done_reason"),
        judge_ms=elapsed_ms,
    )


async def judge_with_anthropic(api_key: str, prompt: str, model: str) -> JudgeOutcome:
    start = time.perf_counter()
    client = AsyncAnthropic(api_key=api_key)
    response = await client.messages.create(
        model=model,
        max_tokens=256,
        tools=[JUDGE_TOOL],
        tool_choice={"type": "tool", "name": "score_answer"},
        messages=judge_messages(prompt),
    )
    tool_use = next(b for b in response.content if b.type == "tool_use")
    result = tool_use.input
    validate_scores(result)
    return JudgeOutcome(
        faithfulness_score=result["faithfulness_score"],
        hallucinated=result["hallucinated"],
        correctness_score=result["correctness_score"],
        raw=json.dumps(result),
        prompt_eval_count=response.usage.input_tokens,
        eval_count=response.usage.output_tokens,
        done_reason=response.stop_reason,
        judge_ms=(time.perf_counter() - start) * 1000,
    )


def judge_call_for(provider: str, config: JudgeConfig, base_url: str, api_key: str = "") -> JudgeCall:
    if provider == "ollama":
        return lambda prompt: judge_with_ollama(base_url, prompt, config)
    return lambda prompt: judge_with_anthropic(api_key, prompt, config.model)


def truncation_status(
    prompt_eval_count: int | None, counted_tokens: int | None, tolerance: int = TRUNCATION_TOLERANCE
) -> str:
    if prompt_eval_count is None or counted_tokens is None:
        return "unchecked"
    return "truncated" if prompt_eval_count < counted_tokens - tolerance else "ok"


def answer_sha1(answer: str) -> str:
    return hashlib.sha1(answer.encode("utf-8")).hexdigest()


async def judge_items(
    records: list[dict],
    config: JudgeConfig,
    call: JudgeCall,
    count_tokens: TokenCounter | None = None,
) -> list[dict]:
    """Judge stored answers in the given order; one judgment record per item.

    With a counter and a fixed context, every prompt is checked before the first call,
    so a run either fits completely or sends nothing.
    """
    prompts = {
        r["id"]: build_judge_prompt(r["question"], judge_context(r), r["answer"], r["reference_answer"])
        for r in records
        if r["chunks"]
    }
    counts = {}
    if count_tokens is not None:
        counts = {item_id: count_tokens(judge_messages(p)) for item_id, p in prompts.items()}
    if counts and not config.legacy:
        over = {i: n for i, n in counts.items() if n + REPLY_RESERVE_TOKENS > config.num_ctx}
        if over:
            raise JudgeContextError(
                f"{len(over)} judge prompts do not fit in num_ctx={config.num_ctx} with "
                f"{REPLY_RESERVE_TOKENS} tokens left for the reply (largest {max(over.values())}): "
                f"{', '.join(sorted(over))}"
            )

    judgments = []
    for order_index, r in enumerate(records):
        # Nothing retrieved: there is nothing to judge faithfulness against (as before v11).
        outcome = await call(prompts[r["id"]]) if r["id"] in prompts else JudgeOutcome()
        counted = counts.get(r["id"])
        truncation = (
            "error" if outcome.error else truncation_status(outcome.prompt_eval_count, counted)
        )
        judgments.append(
            {
                "id": r["id"],
                "dataset": r.get("dataset"),
                "dataset_index": r.get("dataset_index"),
                "run_tag": r.get("run_tag"),
                "judge_label": config.label,
                "judge_model": config.model,
                "judge_num_ctx": config.num_ctx,
                "judge_truncate": None if config.legacy else False,
                "order_index": order_index,
                "answer_sha1": answer_sha1(r["answer"]),
                "prompt_tokens_counted": counted,
                **asdict(outcome),
                "truncation": truncation,
            }
        )
        # One line per item, so a long run's log shows progress (and a stall).
        print(
            f"[judge {config.label} {order_index + 1}/{len(records)}] {r['id']} "
            f"read={outcome.prompt_eval_count} counted={counted} {truncation}"
            + (f" error={outcome.error}" if outcome.error else ""),
            flush=True,
        )
    return judgments

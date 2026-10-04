"""Judge stored answers again, without regenerating them.

Reads per-item generation records written by eval/run_answer_eval.py
(eval/runs/<tag>.gen.jsonl) and writes eval/runs/<tag>.<label>.judge.jsonl plus a report
in eval/reports/. Several files are judged one after another with one judge setting, so
Ollama keeps one model loaded.

Usage:
    python -m eval.run_judge eval/runs/v11_A_test2.gen.jsonl [more .gen.jsonl ...]
        --label J0 --num-ctx 0 [--model qwen2.5:7b-instruct] [--order dataset|reverse]
        [--no-token-count]

--num-ctx 0 sends the pre-v11 judge call (no num_ctx: Ollama's default context, with
over-long prompts cut silently); any other value is sent with truncate=false after
checking that every prompt fits.
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from datetime import UTC, datetime
from pathlib import Path

import httpx

from app.config import get_settings
from eval.answer_report import display_path, render_report
from eval.common import read_json, read_jsonl, write_json, write_jsonl, write_report
from eval.judge import (
    DEFAULT_JUDGE_NUM_CTX,
    JudgeConfig,
    TokenCounter,
    judge_call_for,
    judge_items,
)
from eval.tokens import counter_for_model, tokenizer_source


async def ollama_state(base_url: str) -> dict:
    """Ollama's version, loaded models and local tags, best effort (recorded with results)."""
    state: dict = {}
    async with httpx.AsyncClient(timeout=10.0) as client:
        for key, path in (("version", "/api/version"), ("ps", "/api/ps"), ("tags", "/api/tags")):
            try:
                response = await client.get(f"{base_url.rstrip('/')}{path}")
                response.raise_for_status()
                state[key] = response.json()
            except (httpx.HTTPError, ValueError):
                state[key] = None
    return state


def model_digest(state: dict, model: str) -> str | None:
    """The local model's manifest digest: tags get re-pushed, so a tag alone does not pin it."""
    for local in (state.get("tags") or {}).get("models", []):
        if local.get("name") == model or local.get("model") == model:
            return local.get("digest")
    return None


def context_in_use(state: dict, model: str) -> int | None:
    for loaded in (state.get("ps") or {}).get("models", []):
        if loaded.get("name") == model or loaded.get("model") == model:
            return loaded.get("context_length")
    return None


def judged_path(gen_path: Path, label: str) -> Path:
    stem = gen_path.name.removesuffix(".jsonl").removesuffix(".gen")
    return gen_path.with_name(f"{stem}.{label}.judge.jsonl")


def meta_path(jsonl_path: Path) -> Path:
    return jsonl_path.with_name(jsonl_path.name.removesuffix(".jsonl") + ".meta.json")


def default_label(num_ctx: int | None) -> str:
    return "legacy" if num_ctx is None else f"ctx{num_ctx}"


async def judge_and_save(
    records: list[dict],
    config: JudgeConfig,
    out_path: Path,
    *,
    provider: str,
    base_url: str,
    api_key: str = "",
    count_tokens: TokenCounter | None,
    order: str = "dataset",
) -> tuple[list[dict], dict]:
    """Judge records in the order given, write the judgments and their run notes."""
    started = datetime.now(UTC).isoformat()
    call = judge_call_for(provider, config, base_url, api_key)
    judgments = await judge_items(records, config, call, count_tokens)
    write_jsonl(out_path, judgments)

    state = await ollama_state(base_url) if provider == "ollama" else {}
    source = tokenizer_source(config.model) if count_tokens is not None else None
    judge_meta = {
        "date": started,
        "label": config.label,
        "model": config.model,
        "num_ctx": config.num_ctx,
        "truncate": None if config.legacy else False,
        "provider": provider,
        "order": order,
        "ollama_version": (state.get("version") or {}).get("version"),
        "ollama_ps_after": state.get("ps"),
        "context_in_use": context_in_use(state, config.model),
        "tokenizer": f"{source[0]}@{source[1][:7]}" if source else None,
        "judgments_path": display_path(out_path),
    }
    write_json(meta_path(out_path), judge_meta)
    return judgments, judge_meta


def ordered(records: list[dict], order: str) -> list[dict]:
    records = sorted(records, key=lambda r: r.get("dataset_index", 0))
    return list(reversed(records)) if order == "reverse" else records


async def judge_file(
    gen_path: Path,
    config: JudgeConfig,
    *,
    base_url: str,
    count_tokens: TokenCounter | None,
    order: str = "dataset",
    provider: str = "ollama",
    api_key: str = "",
) -> Path:
    records = ordered(read_jsonl(gen_path), order)
    out_path = judged_path(gen_path, config.label)
    await judge_and_save(
        records,
        config,
        out_path,
        provider=provider,
        base_url=base_url,
        api_key=api_key,
        count_tokens=count_tokens,
        order=order,
    )
    return out_path


async def main(args: argparse.Namespace) -> int:
    settings = get_settings()
    num_ctx = args.num_ctx or None
    errors = 0
    for gen_path in args.generations:
        records = read_jsonl(gen_path)
        model = args.model or records[0].get("model") or settings.ollama_model_name
        config = JudgeConfig(model=model, num_ctx=num_ctx, label=args.label or default_label(num_ctx))
        count_tokens = None
        if not args.no_token_count and settings.generation_provider == "ollama":
            count_tokens = counter_for_model(model)
            if count_tokens is None:
                print(f"warning: no tokenizer mapped for {model}; truncation is not checked")
        out_path = await judge_file(
            gen_path,
            config,
            base_url=settings.ollama_base_url,
            count_tokens=count_tokens,
            order=args.order,
            provider=settings.generation_provider,
            api_key=settings.anthropic_api_key,
        )

        gen_meta = read_json(meta_path(gen_path))
        judgments = read_jsonl(out_path)
        judge_meta = read_json(meta_path(out_path))
        tag = records[0].get("run_tag") or gen_path.stem
        report = render_report(
            f"{tag}, judge {config.label}", gen_meta, ordered(records, "dataset"), judgments, judge_meta
        )
        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        path = write_report(f"answer_eval_{tag}_{config.label}_{timestamp}.md", report)
        errors += sum(1 for j in judgments if j["error"])
        print(f"{gen_path.name}: {len(judgments)} judged -> {display_path(out_path)}, report {path.name}")
    if errors:
        print(f"{errors} judge errors; see the reports", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("generations", type=Path, nargs="+", help="eval/runs/<tag>.gen.jsonl files")
    parser.add_argument("--label", default=None, help="names the output files, e.g. J0 or J1")
    parser.add_argument("--model", default=None, help="defaults to the model that generated the answers")
    parser.add_argument(
        "--num-ctx",
        type=int,
        default=DEFAULT_JUDGE_NUM_CTX,
        help="judge context; 0 sends the pre-v11 call without num_ctx",
    )
    parser.add_argument("--order", choices=["dataset", "reverse"], default="dataset")
    parser.add_argument("--no-token-count", action="store_true", help="skip the tokenizer count")
    sys.stdout.reconfigure(errors="backslashreplace")  # see eval/run_answer_eval.py
    sys.exit(asyncio.run(main(parser.parse_args())))

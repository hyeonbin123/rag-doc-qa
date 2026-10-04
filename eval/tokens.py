"""Token counts for chat prompts, to tell a truncated prompt from a complete one.

Ollama reports prompt_eval_count, the number of prompt tokens the model actually read.
Counting the same chat prompt with the model's own tokenizer and chat template gives the
number it should have read. A prompt Ollama cut comes back far short: on Ollama 0.35.1 an
over-long prompt keeps its first 4 tokens and roughly the last half of the context window.

Only the tokenizer files are downloaded (tens of MB, into the Hugging Face cache), and
only when a run asks for a count; tests pass their own counter.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache


@dataclass(frozen=True)
class TokenizerSpec:
    repo: str
    revision: str
    # "auto": AutoTokenizer. "gpt2": the GPT-2 tokenizer the repo declares (tokenizer.json),
    # for repos that transformers would otherwise load with another model type's
    # pre-tokenizer (see the A.X entry).
    loader: str = "auto"
    # Extra chat-template arguments matching how the model is called.
    template_kwargs: dict = field(default_factory=dict)


# Ollama tag -> Hugging Face repo and pinned revision of the same model's tokenizer.
TOKENIZERS = {
    # Ollama's qwen2.5 template renders a lone user message with the same default system
    # prompt as the Hugging Face chat template ("You are Qwen, created by Alibaba Cloud...").
    "qwen2.5:7b-instruct": TokenizerSpec(
        "Qwen/Qwen2.5-7B-Instruct", "a09a35458c702b33eeacc393d103063234e8bc28"
    ),
    # v13 candidates (docs/experiments.md). qwen3.5 runs with think=false, which both
    # Ollama's renderer and the Hugging Face template render as an empty think block.
    "qwen3.5:9b": TokenizerSpec(
        "Qwen/Qwen3.5-9B",
        "c202236235762e1c871ad0ccb60c8ee5ba337b9a",
        template_kwargs={"enable_thinking": False},
    ),
    "gemma4:12b-it-qat": TokenizerSpec("google/gemma-4-12B-it", "707f0a3b8a3c7ad586ed01e27eafbad8a27dd0f7"),
    # transformers 5.17 loads this repo as Qwen2Tokenizer (from config.json's model_type)
    # and pre-tokenizes with Qwen2's regex; the repo declares GPT2Tokenizer and ships a
    # tokenizer.json with the GPT-2 byte-level regex, which the GGUF conversion follows.
    "a.x-4.0-light:q4_k_m": TokenizerSpec(
        "skt/A.X-4.0-Light", "ba21c20ea1b31ded1ec3e2fb432335077dc4be98", loader="gpt2"
    ),
}


class ChatTokenCounter:
    """Counts the tokens of a chat prompt rendered with the model's chat template."""

    def __init__(self, tokenizer, template_kwargs: dict | None = None) -> None:
        self._tokenizer = tokenizer
        self._template_kwargs = template_kwargs or {}

    def __call__(self, messages: list[dict]) -> int:
        text = self._tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True, **self._template_kwargs
        )
        return len(self._tokenizer(text, add_special_tokens=False)["input_ids"])


def tokenizer_source(model: str) -> tuple[str, str] | None:
    spec = TOKENIZERS.get(model)
    return (spec.repo, spec.revision) if spec else None


def load_tokenizer(spec: TokenizerSpec):
    if spec.loader == "gpt2":
        from transformers import GPT2TokenizerFast  # heavy import, only when counting

        return GPT2TokenizerFast.from_pretrained(spec.repo, revision=spec.revision)
    from transformers import AutoTokenizer

    return AutoTokenizer.from_pretrained(spec.repo, revision=spec.revision)


@lru_cache
def counter_for_model(model: str) -> ChatTokenCounter | None:
    """A counter for an Ollama model tag, or None when its tokenizer is not mapped."""
    spec = TOKENIZERS.get(model)
    if spec is None:
        return None
    return ChatTokenCounter(load_tokenizer(spec), spec.template_kwargs)

"""Token counts for chat prompts, to tell a truncated judge prompt from a complete one.

Ollama reports prompt_eval_count, the number of prompt tokens the model actually read.
Counting the same chat prompt with the model's own tokenizer and chat template gives the
number it should have read. A prompt Ollama cut comes back far short: on Ollama 0.35.1 an
over-long prompt keeps its first 4 tokens and roughly the last half of the context window.

Only the tokenizer files are downloaded (about 11 MB, into the Hugging Face cache), and
only when a judge run asks for a count; tests pass their own counter.
"""

from __future__ import annotations

from functools import lru_cache

# Ollama tag -> Hugging Face repo and pinned revision of the same model's tokenizer.
# Ollama's qwen2.5 template renders a lone user message with the same default system
# prompt as the Hugging Face chat template ("You are Qwen, created by Alibaba Cloud...").
TOKENIZERS = {
    "qwen2.5:7b-instruct": ("Qwen/Qwen2.5-7B-Instruct", "a09a35458c702b33eeacc393d103063234e8bc28"),
}


class ChatTokenCounter:
    """Counts the tokens of a chat prompt rendered with the model's chat template."""

    def __init__(self, tokenizer) -> None:
        self._tokenizer = tokenizer

    def __call__(self, messages: list[dict]) -> int:
        text = self._tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        return len(self._tokenizer(text, add_special_tokens=False)["input_ids"])


def tokenizer_source(model: str) -> tuple[str, str] | None:
    return TOKENIZERS.get(model)


@lru_cache
def counter_for_model(model: str) -> ChatTokenCounter | None:
    """A counter for an Ollama model tag, or None when its tokenizer is not mapped."""
    source = tokenizer_source(model)
    if source is None:
        return None
    from transformers import AutoTokenizer  # heavy import, only when counting

    repo, revision = source
    return ChatTokenCounter(AutoTokenizer.from_pretrained(repo, revision=revision))

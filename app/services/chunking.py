"""Markdown-aware chunker shared by the FastAPI app and the ingestion script.

Splits a markdown document into overlapping chunks of roughly TARGET_TOKENS,
never splitting inside a fenced code block, while tracking a heading
breadcrumb (heading_path) for each chunk.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

import tiktoken

TARGET_TOKENS = 400
MIN_TOKENS = 300
MAX_TOKENS = 500
OVERLAP_TOKENS = 50
HARD_CAP_TOKENS = 1000

_HEADING_RE = re.compile(r"^(#{1,4})\s+(.*)$")
_FENCE_RE = re.compile(r"^\s*```")

_encoding = tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    return len(_encoding.encode(text))


@dataclass
class Line:
    text: str
    heading_path: str


def _annotate_heading_paths(raw_text: str) -> list[Line]:
    """Walk lines, tracking a heading stack, tagging each line with its path."""
    stack: list[tuple[int, str]] = []  # (level, title)
    lines: list[Line] = []
    in_code_block = False

    for raw_line in raw_text.splitlines():
        if _FENCE_RE.match(raw_line):
            in_code_block = not in_code_block
            lines.append(Line(raw_line, _current_path(stack)))
            continue

        if not in_code_block:
            match = _HEADING_RE.match(raw_line)
            if match:
                level = len(match.group(1))
                title = match.group(2).strip()
                while stack and stack[-1][0] >= level:
                    stack.pop()
                stack.append((level, title))

        lines.append(Line(raw_line, _current_path(stack)))

    return lines


def _current_path(stack: list[tuple[int, str]]) -> str:
    return " > ".join(title for _, title in stack)


@dataclass
class ChunkResult:
    content: str
    heading_path: str
    token_count: int


CHUNKER_VERSION = 3

_HEADING_ANCHOR_RE = re.compile(r"\s*\{\s*#[^}]*\}\s*$")
_INCLUDE_DIRECTIVE_RE = re.compile(r"\{\*.*?\*\}")
_ADMONITION_RE = re.compile(r"^\s*/{3,}\s*[\w-]*\s*(?:\|\s*(?P<label>.*))?$")
_TITLED_TERM_RE = re.compile(r"<(dfn|abbr)\s+title=([\"'])(.*?)\2[^>]*>(.*?)</\1>")
_HTML_TAG_RE = re.compile(r"</?[a-zA-Z][^>]*>")


def strip_heading_anchor(text: str) -> str:
    return _HEADING_ANCHOR_RE.sub("", text)


def _strip_outside_inline_code(line: str) -> str:
    parts = line.split("`")
    for i in range(0, len(parts), 2):  # even-indexed parts sit outside inline code spans
        parts[i] = _INCLUDE_DIRECTIVE_RE.sub("", parts[i])
        parts[i] = _TITLED_TERM_RE.sub(r"\4 (\3)", parts[i])
        parts[i] = _HTML_TAG_RE.sub("", parts[i])
    return "`".join(parts)


def clean_markdown(raw_text: str) -> str:
    """Strip MkDocs markup that carries no meaning but dilutes embeddings.

    Removes heading anchor ids, code-include directives, admonition delimiters
    (keeping their labels) and HTML tags. `<dfn>`/`<abbr>` are the exception:
    their title holds a real definition, so they become "term (definition)".
    Fenced code passes through verbatim.
    """
    cleaned: list[str] = []
    in_code_block = False
    for line in raw_text.splitlines():
        if _FENCE_RE.match(line):
            in_code_block = not in_code_block
            cleaned.append(line)
            continue
        if in_code_block:
            cleaned.append(line)
            continue

        if line.lstrip().startswith("#"):
            line = strip_heading_anchor(line)

        admonition = _ADMONITION_RE.match(line)
        if admonition:
            if admonition.group("label"):
                cleaned.append(admonition.group("label").strip())
            continue

        cleaned.append(_strip_outside_inline_code(line))
    return "\n".join(cleaned)


def chunk_markdown(raw_text: str) -> list[ChunkResult]:
    """Chunk a single markdown document into ChunkResult entries."""
    annotated = _annotate_heading_paths(clean_markdown(raw_text))
    if not annotated:
        return []

    chunks: list[ChunkResult] = []
    buffer_lines: list[str] = []
    buffer_tokens = 0
    buffer_heading_path = annotated[0].heading_path
    in_code_block = False
    code_block_lines: list[str] = []

    def flush_buffer() -> None:
        nonlocal buffer_lines, buffer_tokens
        if not buffer_lines:
            return
        content = "\n".join(buffer_lines).strip("\n")
        if content.strip():
            chunks.append(
                ChunkResult(
                    content=content,
                    heading_path=buffer_heading_path,
                    token_count=count_tokens(content),
                )
            )
        buffer_lines = []
        buffer_tokens = 0

    def overlap_tail(lines: list[str]) -> list[str]:
        """Return trailing lines worth ~OVERLAP_TOKENS, for the next chunk's lead-in."""
        tail: list[str] = []
        tokens = 0
        for line in reversed(lines):
            line_tokens = count_tokens(line)
            if tokens + line_tokens > OVERLAP_TOKENS:
                break
            tail.insert(0, line)
            tokens += line_tokens
        return tail

    i = 0
    while i < len(annotated):
        line = annotated[i]

        if _FENCE_RE.match(line.text) and not in_code_block:
            in_code_block = True
            code_block_lines = [line.text]
            i += 1
            while i < len(annotated) and not _FENCE_RE.match(annotated[i].text):
                code_block_lines.append(annotated[i].text)
                i += 1
            if i < len(annotated):
                code_block_lines.append(annotated[i].text)  # closing fence
                i += 1
            in_code_block = False

            code_block_text = "\n".join(code_block_lines)
            code_tokens = count_tokens(code_block_text)

            if code_tokens > HARD_CAP_TOKENS:
                flush_buffer()
                for piece in code_block_text.split("\n\n"):
                    if piece.strip():
                        chunks.append(
                            ChunkResult(
                                content=piece,
                                heading_path=line.heading_path,
                                token_count=count_tokens(piece),
                            )
                        )
                continue

            if buffer_tokens + code_tokens > MAX_TOKENS and buffer_lines:
                flush_buffer()
                buffer_heading_path = line.heading_path

            buffer_lines.append(code_block_text)
            buffer_tokens += code_tokens
            continue

        buffer_lines.append(line.text)
        buffer_tokens += count_tokens(line.text)

        if buffer_tokens >= TARGET_TOKENS:
            flush_buffer()
            tail = overlap_tail(buffer_lines) if buffer_lines else []
            buffer_lines = tail
            buffer_tokens = sum(count_tokens(tail_line) for tail_line in tail)
            buffer_heading_path = annotated[min(i + 1, len(annotated) - 1)].heading_path

        i += 1

    flush_buffer()

    # Merge a final tiny trailing chunk into the previous one, if any.
    if len(chunks) >= 2 and chunks[-1].token_count < MIN_TOKENS // 2:
        last = chunks.pop()
        prev = chunks.pop()
        merged_content = prev.content + "\n\n" + last.content
        chunks.append(
            ChunkResult(
                content=merged_content,
                heading_path=prev.heading_path,
                token_count=count_tokens(merged_content),
            )
        )

    return chunks


def build_embedding_text(heading_path: str, content: str) -> str:
    """Prepend heading breadcrumb to chunk content before embedding."""
    if heading_path:
        return f"{heading_path}\n\n{content}"
    return content

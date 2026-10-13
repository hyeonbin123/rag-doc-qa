"""Markdown-aware chunker shared by the FastAPI app and the ingestion script.

Splits a markdown document into overlapping chunks of roughly TARGET_TOKENS,
never splitting inside a fenced code block, while tracking a heading
breadcrumb (heading_path) for each chunk.
"""

# [파일 역할] FastAPI 문서 마크다운 한 편을 검색 단위인 청크 목록으로 나눈다. 나누기 전에 의미 없는 MkDocs
# 마크업을 걷어 내고(clean_markdown), 각 줄이 어느 절에 속하는지(heading_path)를 추적한 뒤 약 400토큰 단위로
# 자른다(chunk_markdown).
# [왜 이렇게 하나]
# - 마크업 정제: docs/experiments.md v1→v3에서 헤딩 앵커 ID, 코드 include 지시문, admonition, HTML 태그를
#   지우자 MRR이 0.828 → 0.911, dfn·abbr의 정의 글을 살리자 0.933이 됐다. 이런 노이즈가 비슷한 점수의 후보
#   사이에서 순위를 좌우했기 때문이다.
# - 코드 블록은 중간에서 자르지 않는다: 예제 코드가 반으로 갈리면 검색·답변 모두에 쓸모가 줄어든다.
# - heading_path: 청크 앞에 '페이지 제목 > 절' 경로를 붙여 임베딩하고(build_embedding_text), 인용에도 보여
#   준다.
# [연결] 앱의 적재(app/services/ingestion.py)와 CLI 적재(scripts/ingest_fastapi_docs.py)가 같은 이 코드를
# 쓴다. 로직을 바꾸면 CHUNKER_VERSION을 올려야 재적재 때 문서가 다시 처리된다.

from __future__ import annotations

import re
from dataclasses import dataclass

# tiktoken: 청크 크기를 재는 토크나이저. 임베딩 모델의 토크나이저가 아니라 크기를 재는 일정한 단위로만
# 쓴다(BM25 길이 정규화도 이 값을 쓰며, 비율만 쓰므로 단위가 일정하면 된다는 설명이
# app/services/retrieval.py에 있다).
import tiktoken

# 청크 크기 기준(모두 cl100k 토큰 수).
# - TARGET_TOKENS: 일반 줄을 쌓다가 이 값에 닿으면 청크를 끊는다.
# - MIN_TOKENS: 마지막 청크가 이 값의 절반(150) 미만이면 앞 청크에 합친다.
# - MAX_TOKENS: 코드 블록을 붙였을 때 이 값을 넘으면 먼저 지금까지를 끊고 코드 블록을 새 청크로 시작한다.
# - OVERLAP_TOKENS: 다음 청크 앞에 이전 청크 끝 약 50토큰을 겹쳐 넣으려는 값. 단, 아래 chunk_markdown 주석처럼
#   지금 코드에서는 실제로 적용되지 않는다.
# - HARD_CAP_TOKENS: 이보다 긴 코드 블록은 어쩔 수 없이 빈 줄 기준으로 쪼갠다.
TARGET_TOKENS = 400
MIN_TOKENS = 300
MAX_TOKENS = 500
OVERLAP_TOKENS = 50
HARD_CAP_TOKENS = 1000

# _HEADING_RE: # ~ #### 헤딩 줄(레벨, 제목). 다섯 단계 이상은 일반 줄로 본다. _FENCE_RE: 코드 펜스(```로
# 시작하는 줄, 앞 공백 허용).
_HEADING_RE = re.compile(r"^(#{1,4})\s+(.*)$")
_FENCE_RE = re.compile(r"^\s*```")

# 인코딩 객체를 모듈을 불러올 때 한 번만 만들어 재사용한다.
_encoding = tiktoken.get_encoding("cl100k_base")


# 문자열의 cl100k 토큰 수. 청크 크기 판단과 chunks.token_count 저장에 쓴다.
def count_tokens(text: str) -> int:
    return len(_encoding.encode(text))


# 정제한 문서의 한 줄과, 그 줄이 속한 헤딩 경로.
@dataclass
class Line:
    text: str
    heading_path: str


# 줄마다 헤딩 경로를 붙인다. 헤딩을 만나면 같은 레벨 이상(같거나 더 깊은) 항목을 스택에서 빼고 새 제목을
# 넣는다. 예: '# A' 아래 '## B' 다음 '## C'가 오면 경로가 'A > B'에서 'A > C'로 바뀐다.
# 코드 블록 안에서는 헤딩을 인식하지 않는다. 파이썬 주석('# ...')처럼 #으로 시작하는 코드 줄을 헤딩으로
# 착각하지 않게 하려는 것이다.
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


# 스택의 제목들을 ' > '로 이어 'Tutorial > Path Parameters' 같은 경로를 만든다.
def _current_path(stack: list[tuple[int, str]]) -> str:
    return " > ".join(title for _, title in stack)


# 청크 하나의 결과: 본문, 헤딩 경로, 토큰 수. 적재가 이것으로 Chunk 행을 만든다.
@dataclass
class ChunkResult:
    content: str
    heading_path: str
    token_count: int


# 청커 버전. 적재 해시에 들어가므로 청킹·정제 로직을 바꾸면 이 값을 올려야 한다. 원문만 해시하면 청커를 바꿔도
# 모든 문서가 '변경 없음'으로 건너뛰어져 예전 청크로 측정하게 되는 잠재 버그가 있었다(docs/experiments.md
# v1→v3).
CHUNKER_VERSION = 3

# 정제용 정규식들(MkDocs 문법).
# - _HEADING_ANCHOR_RE: 헤딩 끝의 앵커 ID 표기(중괄호 안에 # 아이디). 그대로 두면 제목이 임베딩에 두 번
#   들어가는 것과 같은 노이즈가 된다.
# - _INCLUDE_DIRECTIVE_RE: 중괄호+별표로 감싼 코드 include 지시문. 실제 코드 없이 파일 경로만 있어 의미가
#   없다.
# - _ADMONITION_RE: 슬래시 세 개 이상으로 여닫는 admonition 블록 경계 줄. '|' 뒤의 라벨(예: 팁 제목)은 살린다.
# - _TITLED_TERM_RE: title 속성이 있는 dfn·abbr 태그. title에 진짜 정의가 있어 '용어 (정의)'로 바꾼다.
# - _HTML_TAG_RE: 나머지 HTML 태그(태그만 지우고 안의 글은 남긴다).
_HEADING_ANCHOR_RE = re.compile(r"\s*\{\s*#[^}]*\}\s*$")
_INCLUDE_DIRECTIVE_RE = re.compile(r"\{\*.*?\*\}")
_ADMONITION_RE = re.compile(r"^\s*/{3,}\s*[\w-]*\s*(?:\|\s*(?P<label>.*))?$")
_TITLED_TERM_RE = re.compile(r"<(dfn|abbr)\s+title=([\"'])(.*?)\2[^>]*>(.*?)</\1>")
_HTML_TAG_RE = re.compile(r"</?[a-zA-Z][^>]*>")


# 헤딩 끝의 앵커 ID를 지운다. 적재가 페이지 제목을 뽑을 때(app/services/ingestion.py의 extract_title)도 쓴다.
def strip_heading_anchor(text: str) -> str:
    return _HEADING_ANCHOR_RE.sub("", text)


# 한 줄에서 백틱(`)으로 감싼 인라인 코드 밖에서만 정제한다. 백틱으로 나누면 짝수 번째 조각이 코드 밖이다.
# 문서가 HTML 태그나 include 문법 자체를 인라인 코드로 설명하는 경우 그 예시를 지우지 않으려는
# 것이다(tests/test_chunking.py에 이 경우 테스트가 있다).
# 순서: include 지시문 삭제 → dfn·abbr를 '용어 (정의)'로 → 남은 태그 삭제. 태그를 먼저 지우면 정의 글이
# 사라지므로 이 순서가 중요하다(v2에서 title까지 지워 q011이 회귀한 원인).
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
    # 코드 펜스 안의 줄은 손대지 않고 그대로 둔다. 코드 예제는 한 글자도 바꾸면 안 되기 때문이다.
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

        # 헤딩 줄에서만 앵커 ID를 지운다.
        if line.lstrip().startswith("#"):
            line = strip_heading_anchor(line)

        # admonition 경계 줄은 버리고, 라벨이 있으면 라벨 글만 한 줄로 남긴다.
        admonition = _ADMONITION_RE.match(line)
        if admonition:
            if admonition.group("label"):
                cleaned.append(admonition.group("label").strip())
            continue

        cleaned.append(_strip_outside_inline_code(line))
    return "\n".join(cleaned)


# 정제 → 헤딩 경로 표시 → 토큰 수 기준으로 줄을 모아 청크를 만든다.
# - 일반 줄: 버퍼에 쌓다가 TARGET_TOKENS에 닿으면 끊는다.
# - 코드 블록: 여는 펜스부터 닫는 펜스까지를 한 덩어리로 다룬다. 버퍼에 붙여 MAX_TOKENS를 넘으면 먼저 끊는다.
#   HARD_CAP_TOKENS보다 길면 따로 빈 줄 기준으로 쪼갠다.
# - 마지막 청크가 너무 작으면 앞 청크에 합친다.
# 청크의 heading_path는 그 청크 첫 줄의 절이다. 여러 절에 걸친 청크도 첫 절 경로만 갖는다.
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

    # 버퍼의 줄을 하나의 청크로 확정하고 버퍼를 비운다. 앞뒤 빈 줄은 떼고, 공백뿐이면 청크를 만들지 않는다.
    # 토큰 수는 합친 본문으로 다시 센다.
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

    # 줄 목록의 끝에서부터 OVERLAP_TOKENS를 넘지 않을 만큼의 줄을 돌려준다(다음 청크 앞머리로 겹쳐 넣을 부분).
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

        # 코드 블록 시작: 닫는 펜스까지 한 번에 모은다. 닫는 펜스가 없으면 문서 끝까지가 코드 블록이다.
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

            # 아주 긴 코드 블록: 지금까지의 버퍼를 먼저 확정하고, 블록을 빈 줄 기준으로 나눠 조각마다 청크로
            # 만든다. 조각 크기를 다시 제한하지는 않는다.
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

            # 코드 블록을 붙이면 너무 커질 때: 지금까지를 끊고, 코드 블록이 새 청크의 시작이 되며 그 헤딩
            # 경로를 따른다. 그렇지 않으면 코드 블록 전체를 버퍼에 그대로 붙인다.
            if buffer_tokens + code_tokens > MAX_TOKENS and buffer_lines:
                flush_buffer()
                buffer_heading_path = line.heading_path

            buffer_lines.append(code_block_text)
            buffer_tokens += code_tokens
            continue

        buffer_lines.append(line.text)
        buffer_tokens += count_tokens(line.text)

        # 목표 크기에 닿으면 끊고, 다음 청크의 헤딩 경로를 다음 줄의 경로로 바꾼다.
        # 주의: flush_buffer()가 이미 buffer_lines를 비운 뒤라 overlap_tail에 넘길 줄이 없어 tail은 항상 빈
        # 목록이다. 그래서 OVERLAP_TOKENS 겹침은 실제로 적용되지 않고, 모듈 docstring의 'overlapping chunks'와
        # 다르다. 고치면 청크가 바뀌므로 CHUNKER_VERSION을 올리고 재적재·재측정해야 한다.
        if buffer_tokens >= TARGET_TOKENS:
            flush_buffer()
            tail = overlap_tail(buffer_lines) if buffer_lines else []
            buffer_lines = tail
            buffer_tokens = sum(count_tokens(tail_line) for tail_line in tail)
            buffer_heading_path = annotated[min(i + 1, len(annotated) - 1)].heading_path

        i += 1

    flush_buffer()

    # Merge a final tiny trailing chunk into the previous one, if any.
    # 문서 끝에 150토큰 미만의 작은 청크가 남으면 앞 청크에 합친다. 내용이 거의 없는 청크가 따로 검색되는 것을
    # 막는다. 합친 청크는 앞 청크의 헤딩 경로를 쓴다.
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


# 임베딩·재정렬에 넣을 글: '헤딩 경로 + 빈 줄 + 본문'. 본문에 절 제목 단어가 없어도 어느 절의 내용인지가
# 벡터에 반영된다. 적재(app/services/ingestion.py), cross-encoder 입력(app/services/retrieval.py의
# rerank_search), 벡터 확인(eval/retrieval_checks.py)이 모두 이 함수를 써서 같은 입력을 만든다.
def build_embedding_text(heading_path: str, content: str) -> str:
    """Prepend heading breadcrumb to chunk content before embedding."""
    if heading_path:
        return f"{heading_path}\n\n{content}"
    return content

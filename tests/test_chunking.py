# [테스트 묶음] 청커(app/services/chunking.py)의 단위 테스트. DB 없이 순수 함수만 검사한다: 헤딩 경로 보존,
# 코드 블록을 자르지 않음, 임베딩 입력에 머리말 붙이기, 토큰 수 세기, MkDocs 마크업 정제.
# [왜 중요한가] 검색 품질의 첫 개선(v1 → v3, MRR 0.828 → 0.933)이 이 정제에서 나왔다. 헤딩 앵커 { #id }는
# 제목을 임베딩에 두 번 넣었고, 경로만 있는 include 지시문은 노이즈였으며, v2에서 <dfn> title까지 지워 q011이
# 1위에서 3위로 떨어졌다(docs/experiments.md v1 → v3). 이 테스트들이 그 동작을 고정한다.

import pytest

import app.services.chunking as chunking
from app.services.chunking import (
    CHUNKER_VERSION,
    HARD_CAP_TOKENS,
    MIN_TOKENS,
    OVERLAP_TOKENS,
    TARGET_TOKENS,
    build_embedding_text,
    chunk_markdown,
    clean_markdown,
    count_tokens,
    strip_heading_anchor,
)

# 제목 2단계와 Python 코드 블록이 들어 있는 짧은 FastAPI 문서 예시. 헤딩 경로와 코드 블록 보존 테스트가 함께
# 쓴다.
SAMPLE_DOC = """# Path Parameters

You can declare path parameters with the same syntax used by Python format strings.

## Data types

You can declare the type of a path parameter using standard Python type annotations.

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}
```

Here `item_id` is declared as an `int`.

## Order matters

When creating path operations, you can find situations where you have a fixed path.
"""


# 청크마다 붙는 heading_path에 문서 제목이 남는지 확인한다. 인용 제목과 임베딩 머리말이 이 값에서 나온다.
def test_chunk_markdown_preserves_all_headings():
    chunks = chunk_markdown(SAMPLE_DOC)
    assert len(chunks) >= 1
    heading_paths = {c.heading_path for c in chunks}
    assert any("Path Parameters" in hp for hp in heading_paths)


# 코드 블록 안의 줄이 청크 경계에서 잘리지 않고 온전히 남는지 확인한다. 코드가 반으로 잘리면 검색된 청크만으로
# 답을 만들 수 없다.
def test_chunk_markdown_never_splits_inside_code_fence():
    chunks = chunk_markdown(SAMPLE_DOC)
    combined = "\n\n".join(c.content for c in chunks)
    # 코드 블록이 합친 결과의 어딘가에 온전한 모양으로 나와야 한다
    assert "async def read_item(item_id: int):" in combined
    assert "return {\"item_id\": item_id}" in combined


# 빈 문서는 청크를 만들지 않는다(빈 청크가 DB와 검색 결과에 들어가지 않게).
def test_chunk_markdown_empty_input_returns_no_chunks():
    assert chunk_markdown("") == []


# 임베딩 입력은 헤딩 경로를 앞에 붙인 본문이다. 본문만으로는 어느 절의 내용인지 드러나지 않는 청크도 제목으로
# 찾을 수 있게 한다.
def test_build_embedding_text_prepends_heading():
    text = build_embedding_text("Tutorial > Path Params", "some content")
    assert text.startswith("Tutorial > Path Params")
    assert "some content" in text


# 헤딩이 없으면 본문을 그대로 쓴다(빈 줄만 앞에 붙지 않게).
def test_build_embedding_text_no_heading():
    text = build_embedding_text("", "some content")
    assert text == "some content"


# 토큰 수(tiktoken cl100k_base 기준)가 비어 있지 않은 글에서는 0보다 크고 빈 글에서는 0. 청크 크기 상한과
# BM25의 문서 길이에 쓰이는 값이다.
def test_count_tokens_nonzero_for_nonempty_text():
    assert count_tokens("hello world") > 0
    assert count_tokens("") == 0


# MkDocs 헤딩 앵커 { #id }를 떼고, 앵커가 없는 헤딩은 그대로 둔다.
def test_strip_heading_anchor():
    assert strip_heading_anchor("# Path Parameters { #path-parameters }") == "# Path Parameters"
    assert strip_heading_anchor("# No Anchor Here") == "# No Anchor Here"


# 정제가 MkDocs 전용 마크업(앵커, 장식용 div, /// 박스 표시, 코드 include 지시문)은 지우고, 박스 안의 본문과
# 박스 제목('Technical Details')은 남기는지 확인한다.
def test_clean_markdown_removes_mkdocs_markup_but_keeps_prose():
    raw = "\n".join(
        [
            "## Install { #install }",
            '<div class="termy">',
            "/// tip",
            "Use `uv` to install it.",
            "///",
            "/// note | Technical Details",
            "{* ../../docs_src/app/main.py hl[3] *}",
            "</div>",
        ]
    )
    cleaned = clean_markdown(raw)
    assert "{ #install }" not in cleaned
    assert "termy" not in cleaned
    assert "docs_src" not in cleaned
    assert "///" not in cleaned
    assert "Use `uv` to install it." in cleaned
    assert "Technical Details" in cleaned


# 코드 블록 안은 HTML·지시문·헤딩처럼 보여도 한 글자도 바꾸지 않아야 한다. 코드 예시가 망가지면 답변에 틀린
# 코드가 들어간다.
def test_clean_markdown_leaves_code_fences_untouched():
    raw = '```html\n<div class="x">{* not-a-directive *}</div>\n# not a heading { #x }\n```'
    assert clean_markdown(raw) == raw


# 인라인 코드 안의 HTML 태그도 지우지 않는다.
def test_clean_markdown_keeps_html_inside_inline_code():
    assert clean_markdown("Return `<b>bold</b>` directly.") == "Return `<b>bold</b>` directly."


# 청크의 heading_path에도 앵커가 남지 않아야 한다. 남으면 머리말을 통해 임베딩에 노이즈가 다시 들어간다.
def test_heading_path_has_no_anchor_ids():
    chunks = chunk_markdown("# Top { #top }\n\n## Sub { #sub }\n\nSome prose here.")
    assert chunks
    assert all("{ #" not in c.heading_path for c in chunks)


# v3의 수정을 고정한다: <dfn>·<abbr>의 title 속성은 지우지 않고 '용어 (정의)' 형태로 남긴다. v2에서 이 정의
# 텍스트('cleanup code')를 지워 q011이 회귀했었다.
def test_clean_markdown_keeps_definition_text_from_dfn_and_abbr():
    raw = (
        "Dependencies can do some <dfn title='also called \"cleanup code\"'>extra steps</dfn>, "
        'using an <abbr title="Object Relational Mapper">ORM</abbr>.'
    )
    cleaned = clean_markdown(raw)
    assert 'extra steps (also called "cleanup code")' in cleaned
    assert "ORM (Object Relational Mapper)" in cleaned
    assert "<" not in cleaned


# --- 청크 겹침 (docs/experiments.md v14) ---
# CHUNKER_VERSION 4에서 겹침이 실제로 적용되게 고쳤고, v14 재측정 결과로 5에서 겹침을 껐다
# (OVERLAP_TOKENS = 0). 기본 청커는 겹치지 않는 청크를 만들고, 그 청크는 3까지와 같다. 겹침을 다시 켜는
# 경우를 위해 고친 겹침 동작은 아래 overlap_on 픽스처(OVERLAP_TOKENS = 50, v14에서 잰 값)로 계속 고정한다.

# 서로 다른 짧은 줄(줄마다 약 11토큰). 줄이 모두 달라서 어느 줄이 어느 청크에 몇 번 들어갔는지 셀 수 있다.
SHORT_LINES = [f"Line {i:03d} says one short thing about path parameters." for i in range(200)]

# v14에서 재 본 겹침 크기.
MEASURED_OVERLAP_TOKENS = 50


@pytest.fixture
def overlap_on(monkeypatch):
    monkeypatch.setattr(chunking, "OVERLAP_TOKENS", MEASURED_OVERLAP_TOKENS)


# 기본값은 겹침 꺼짐이다. 청커 버전 5는 4로 적재한 DB가 다음 적재 때 다시 처리되게 하려고 올렸고, 6은 청크의
# heading_path를 바로잡은 판이다(아래 'heading_path는 청크에 실제로 들어간 첫 비공백 줄의 절' 절).
def test_overlap_is_off_by_default():
    assert OVERLAP_TOKENS == 0
    assert CHUNKER_VERSION == 6


# 겹침이 꺼져 있으면 청크를 이어 붙인 줄이 문서의 줄과 같아야 한다(빈 줄을 빼고, 줄마다 한 번씩, 순서대로).
# 앞 청크 끝의 줄이 다음 청크에 다시 들어가면 실패한다.
def test_default_chunks_do_not_overlap():
    chunks = chunk_markdown("\n".join(SHORT_LINES))

    assert len(chunks) >= 3
    joined = [line for c in chunks for line in c.content.split("\n") if line]
    assert joined == SHORT_LINES


# 줄을 앞에서부터 쌓아 토큰 합이 처음으로 TARGET_TOKENS에 닿는 줄 수. 청커는 줄마다 센 토큰을 더해 끊을 때를
# 정하므로 같은 방식으로 센다.
def _lines_to_reach_target() -> int:
    total = 0
    for n, line in enumerate(SHORT_LINES, start=1):
        total += count_tokens(line)
        if total >= TARGET_TOKENS:
            return n
    raise AssertionError("SHORT_LINES is too short")


# 목표 크기에서 끊긴 청크 다음 청크는 앞 청크 끝의 줄(OVERLAP_TOKENS 이하)로 시작해야 한다. CHUNKER_VERSION
# 3까지는 겹칠 줄을 버퍼를 비운 뒤에 골라 다음 청크가 늘 새 줄로 시작했다.
@pytest.mark.usefixtures("overlap_on")
def test_a_chunk_cut_at_the_target_size_overlaps_the_next_one():
    chunks = chunk_markdown("\n".join(SHORT_LINES))

    assert len(chunks) >= 3
    for prev, cur in zip(chunks, chunks[1:], strict=False):
        prev_lines = prev.content.split("\n")
        lead = [line for line in cur.content.split("\n") if line in prev_lines]
        assert lead, "the next chunk repeats none of the previous chunk's lines"
        assert prev_lines[-len(lead) :] == lead == cur.content.split("\n")[: len(lead)]
        assert sum(count_tokens(line) for line in lead) <= MEASURED_OVERLAP_TOKENS


# 문서가 목표 크기에 닿는 줄에서 바로 끝나면, 겹쳐 둔 줄만 남는다. 그 줄들로 청크를 만들면 앞 청크 끝을
# 되풀이할 뿐이고(끝의 작은 청크로 합쳐지면 한 청크 안에 같은 줄이 두 번 들어간다) 새 내용이 없으므로 청크를
# 만들지 않는다.
@pytest.mark.usefixtures("overlap_on")
def test_overlap_lines_alone_never_make_a_chunk():
    lines = SHORT_LINES[: _lines_to_reach_target()]

    chunks = chunk_markdown("\n".join(lines))

    assert [c.content.split("\n") for c in chunks] == [lines]


# 끝에 남은 작은 청크(150토큰 미만)를 앞 청크에 합칠 때, 앞 청크 끝과 겹치는 줄은 다시 붙이지 않는다. 합친
# 청크에는 문서의 줄이 순서대로 한 번씩만 들어 있어야 한다.
@pytest.mark.usefixtures("overlap_on")
def test_a_small_trailing_chunk_merges_without_repeating_the_overlap():
    lines = SHORT_LINES[: _lines_to_reach_target() + 3]

    chunks = chunk_markdown("\n".join(lines))

    assert len(chunks) == 1
    assert [line for line in chunks[0].content.split("\n") if line] == lines


# --- heading_path는 청크에 실제로 들어간 첫 비공백 줄의 절 (docs/experiments.md v16-A) ---
# CHUNKER_VERSION 5까지는 목표 크기에서 끊은 다음 청크의 경로를, 끊은 직후 '다음 줄 하나'의 경로로
# 미리 정했다. 마크다운에서 새 절은 보통 빈 줄 뒤에 헤딩이 오므로 그 빈 줄(아직 옛 절)의 경로가 붙어,
# 헤딩으로 시작하는 청크의 heading_path가 한 절 뒤처졌다(본 DB 청크 1,535개 중 231개). 1,000토큰을 넘는
# 코드 블록(HARD_CAP_TOKENS)을 조각낸 뒤에는 경로를 갱신하지 않아 그 다음 청크도 옛 경로를 달았다. 이 값은
# 임베딩 머리말(build_embedding_text), BM25의 tsvector, 생성 프롬프트의 '[N] (경로)', 화면의 인용 제목에
# 그대로 쓰인다. 아래 테스트는 "청크의 heading_path == 그 청크에 실제로 들어간 첫 비공백 줄(또는 코드 블록)의
# 절 경로"를 고정한다. 처음 두 테스트와 속성 테스트의 target_cut·hard_cap·parts·leading_blank 문서는 고치기 전
# 코드에서 실패하는 것을 확인했다.

# 한 줄로 쓴 긴 문단(400토큰 넘음). 이 줄을 버퍼에 더하는 순간 목표 크기에 닿아 청크가 끊기고, 다음 청크는
# 빈 줄과 다음 절의 헤딩으로 시작한다.
LONG_PARAGRAPH = " ".join(
    f"Sentence {i} of section A explains one more detail of path parameters." for i in range(60)
)

# 다음 절의 본문(150토큰 이상). 끝의 작은 청크(MIN_TOKENS // 2 미만)는 앞 청크에 합쳐지므로, 그 합치기에
# 걸리지 않을 만큼 길어야 헤딩으로 시작하는 청크가 따로 남는다.
SECTION_B_BODY = "\n".join(
    f"Section B line {i} describes the next topic in its own words." for i in range(20)
)

# 1,000토큰을 넘는 코드 블록. 빈 줄로 나뉜 문장들이라 HARD_CAP 분기가 빈 줄 기준으로 조각낸다.
HARD_CAPPED_CODE = (
    "```python\n"
    + "\n\n".join(f"value_{i} = compute_{i}(argument_{i}, other_{i})" for i in range(120))
    + "\n```"
)

# 버퍼에 붙이면 MAX_TOKENS(500)를 넘지만 혼자서는 HARD_CAP에 못 미치는 코드 블록(약 350토큰). 앞 버퍼를
# 끊고 새 청크의 시작이 되는 경우를 만든다.
MEDIUM_CODE = "```python\n" + "\n".join(f"item_{i} = make_item({i})" for i in range(60)) + "\n```"


# 절마다 줄을 쌓아 그 절의 마지막 줄에서 정확히 목표 크기에 닿게 만든 문서. 청커는 끊은 뒤 0부터, 줄마다
# 센 토큰을 더해 끊을 때를 정하므로 같은 방식으로 센다(빈 줄은 0토큰). 그러면 절이 끝나는 줄에서 청크가
# 끊기고, 다음 청크는 빈 줄과 다음 절의 헤딩으로 시작한다(고치기 전 코드가 옛 절 경로를 달던 자리).
def _parts_doc() -> str:
    parts = ["# Guide"]
    total = count_tokens("# Guide")
    lines = iter(SHORT_LINES)
    for k in range(4):
        heading = f"## Part {k}"
        body: list[str] = []
        total += count_tokens(heading)
        while total < TARGET_TOKENS:
            line = next(lines)
            body.append(line)
            total += count_tokens(line)
        parts.append("\n".join([heading, "", *body]))
        total = 0
    return "\n\n".join(parts) + "\n"


# 청크마다 '그 청크에 실제로 들어간 첫 비공백 줄'이 헤딩 경로를 매기는 함수에서 가진 경로를 구한다. 청크는
# 문서 순서대로 나오므로 앞 청크 뒤에서부터 같은 글의 줄을 찾고, 코드 펜스처럼 되풀이되는 줄이 있어도
# 앞 청크 안의 줄로 되돌아가지 않게 커서를 청크 끝으로 옮긴다.
def _expected_heading_paths(doc: str, chunks) -> list[str]:
    annotated = chunking._annotate_heading_paths(chunking.clean_markdown(doc))
    expected = []
    cursor = 0
    for chunk in chunks:
        lines = chunk.content.split("\n")
        k, first = next((k, line) for k, line in enumerate(lines) if line.strip())
        j = next(j for j in range(cursor, len(annotated)) if annotated[j].text == first)
        expected.append(annotated[j].heading_path)
        cursor = max(j + 1, j - k + len(lines))
    return expected


# 긴 문단 뒤에서 끊긴 다음 청크가 '## B'로 시작하면 그 경로는 'T > B'다. 고치기 전에는 끊은 직후의 빈 줄 경로
# 'T > A'가 붙었다.
def test_a_chunk_that_starts_with_a_heading_gets_that_headings_path():
    assert count_tokens(LONG_PARAGRAPH) > TARGET_TOKENS
    assert count_tokens(SECTION_B_BODY) >= MIN_TOKENS // 2
    doc = f"# T\n\n## A\n\n{LONG_PARAGRAPH}\n\n## B\n\n{SECTION_B_BODY}\n"

    chunks = chunk_markdown(doc)

    b_chunks = [c for c in chunks if c.content.startswith("## B")]
    assert len(b_chunks) == 1
    assert b_chunks[0].heading_path == "T > B"


# 1,000토큰을 넘는 코드 블록을 조각낸 뒤에 오는 본문 청크도 그 절('T > B')의 경로를 가진다. 고치기 전에는
# 코드 블록 앞 버퍼의 경로('T')가 그대로 남았다. 조각들은 그 전에도 코드 블록이 속한 절의 경로를 가졌다.
def test_the_chunk_after_a_hard_capped_code_block_keeps_its_sections_path():
    assert count_tokens(HARD_CAPPED_CODE) > HARD_CAP_TOKENS
    doc = f"# T\n\n## B\n\n{HARD_CAPPED_CODE}\n\n{SECTION_B_BODY}\n"

    chunks = chunk_markdown(doc)

    body_chunks = [c for c in chunks if c.content.startswith("Section B line 0")]
    assert len(body_chunks) == 1
    assert body_chunks[0].heading_path == "T > B"
    assert all(c.heading_path == "T > B" for c in chunks if c.content.startswith("value_"))


# 합성 문서들. 모든 청크의 heading_path가 그 청크에 실제로 들어간 첫 비공백 줄의 경로와 같아야 한다.
# - parts: 절이 끝나는 줄에서 끊겨 다음 청크가 빈 줄 + 헤딩으로 시작하는 자리가 세 번 있다
# - leading_blank: 문서가 빈 줄로 시작한다(첫 청크의 경로는 첫 줄이 아니라 첫 비공백 줄의 것이어야 함)
# - code_opens_chunk: 버퍼에 붙이면 MAX_TOKENS를 넘는 코드 블록이 새 청크를 시작한다
# - trailing_merge: 끝의 작은 청크가 앞 청크에 합쳐진다(합친 청크는 앞 청크 첫 줄의 경로)
_SYNTHETIC_DOCS = {
    "sample": SAMPLE_DOC,
    "target_cut": f"# T\n\n## A\n\n{LONG_PARAGRAPH}\n\n## B\n\n{SECTION_B_BODY}\n",
    "hard_cap": f"# T\n\n## B\n\n{HARD_CAPPED_CODE}\n\n{SECTION_B_BODY}\n",
    "parts": _parts_doc(),
    "leading_blank": f"\n\n# Title\n\nIntro line.\n\n## Sub\n\n{SECTION_B_BODY}\n",
    "code_opens_chunk": f"# T\n\n## A\n\n{SECTION_B_BODY}\n\n## C\n\n{MEDIUM_CODE}\n\n{SECTION_B_BODY}\n",
    "trailing_merge": f"# T\n\n## A\n\n{LONG_PARAGRAPH}\n\n## B\n\nOne short closing line.\n",
}


@pytest.mark.parametrize("name", sorted(_SYNTHETIC_DOCS))
def test_every_chunk_path_is_the_path_of_its_first_nonblank_line(name):
    doc = _SYNTHETIC_DOCS[name]

    chunks = chunk_markdown(doc)

    assert chunks
    assert [c.heading_path for c in chunks] == _expected_heading_paths(doc, chunks)

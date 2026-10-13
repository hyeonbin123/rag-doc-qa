# [테스트 묶음] 청커(app/services/chunking.py)의 단위 테스트. DB 없이 순수 함수만 검사한다: 헤딩 경로 보존,
# 코드 블록을 자르지 않음, 임베딩 입력에 머리말 붙이기, 토큰 수 세기, MkDocs 마크업 정제.
# [왜 중요한가] 검색 품질의 첫 개선(v1 → v3, MRR 0.828 → 0.933)이 이 정제에서 나왔다. 헤딩 앵커 { #id }는
# 제목을 임베딩에 두 번 넣었고, 경로만 있는 include 지시문은 노이즈였으며, v2에서 <dfn> title까지 지워 q011이
# 1위에서 3위로 떨어졌다(docs/experiments.md v1 → v3). 이 테스트들이 그 동작을 고정한다.

from app.services.chunking import (
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
    # the code block should appear intact somewhere in the combined output
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

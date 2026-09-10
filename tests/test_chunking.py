from app.services.chunking import (
    build_embedding_text,
    chunk_markdown,
    clean_markdown,
    count_tokens,
    strip_heading_anchor,
)

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


def test_chunk_markdown_preserves_all_headings():
    chunks = chunk_markdown(SAMPLE_DOC)
    assert len(chunks) >= 1
    heading_paths = {c.heading_path for c in chunks}
    assert any("Path Parameters" in hp for hp in heading_paths)


def test_chunk_markdown_never_splits_inside_code_fence():
    chunks = chunk_markdown(SAMPLE_DOC)
    combined = "\n\n".join(c.content for c in chunks)
    # the code block should appear intact somewhere in the combined output
    assert "async def read_item(item_id: int):" in combined
    assert "return {\"item_id\": item_id}" in combined


def test_chunk_markdown_empty_input_returns_no_chunks():
    assert chunk_markdown("") == []


def test_build_embedding_text_prepends_heading():
    text = build_embedding_text("Tutorial > Path Params", "some content")
    assert text.startswith("Tutorial > Path Params")
    assert "some content" in text


def test_build_embedding_text_no_heading():
    text = build_embedding_text("", "some content")
    assert text == "some content"


def test_count_tokens_nonzero_for_nonempty_text():
    assert count_tokens("hello world") > 0
    assert count_tokens("") == 0


def test_strip_heading_anchor():
    assert strip_heading_anchor("# Path Parameters { #path-parameters }") == "# Path Parameters"
    assert strip_heading_anchor("# No Anchor Here") == "# No Anchor Here"


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


def test_clean_markdown_leaves_code_fences_untouched():
    raw = '```html\n<div class="x">{* not-a-directive *}</div>\n# not a heading { #x }\n```'
    assert clean_markdown(raw) == raw


def test_clean_markdown_keeps_html_inside_inline_code():
    assert clean_markdown("Return `<b>bold</b>` directly.") == "Return `<b>bold</b>` directly."


def test_heading_path_has_no_anchor_ids():
    chunks = chunk_markdown("# Top { #top }\n\n## Sub { #sub }\n\nSome prose here.")
    assert chunks
    assert all("{ #" not in c.heading_path for c in chunks)


def test_clean_markdown_keeps_definition_text_from_dfn_and_abbr():
    raw = (
        "Dependencies can do some <dfn title='also called \"cleanup code\"'>extra steps</dfn>, "
        'using an <abbr title="Object Relational Mapper">ORM</abbr>.'
    )
    cleaned = clean_markdown(raw)
    assert 'extra steps (also called "cleanup code")' in cleaned
    assert "ORM (Object Relational Mapper)" in cleaned
    assert "<" not in cleaned

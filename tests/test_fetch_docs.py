"""scripts/fetch_docs.py, the debug listing of the pages an ingest would pick up."""

import httpx
import pytest

from scripts import fetch_docs

TREE = {
    "tree": [
        {"path": "docs/en/docs/index.md", "type": "blob"},
        {"path": "docs/ko/docs/index.md", "type": "blob"},
        {"path": "docs/ko/docs/translation-banner.md", "type": "blob"},
    ]
}


@pytest.fixture(autouse=True)
def github_tree(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path.endswith("/git/trees/deadbeef")
        return httpx.Response(200, json=TREE)

    real_client = httpx.AsyncClient
    monkeypatch.setattr(
        fetch_docs.httpx,
        "AsyncClient",
        lambda **kwargs: real_client(transport=httpx.MockTransport(handler), **kwargs),
    )


@pytest.mark.asyncio
async def test_fetch_docs_lists_the_pages_of_every_language(capsys):
    await fetch_docs.main("deadbeef")

    out = capsys.readouterr().out
    assert "doc files found: 2" in out
    assert "[en] docs/en/docs/index.md" in out
    assert "[ko] docs/ko/docs/index.md" in out
    assert "translation-banner.md" not in out


@pytest.mark.asyncio
async def test_fetch_docs_can_list_one_language(capsys):
    await fetch_docs.main("deadbeef", ("en",))

    out = capsys.readouterr().out
    assert "doc files found: 1" in out
    assert "docs/ko/" not in out

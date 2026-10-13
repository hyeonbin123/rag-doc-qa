"""scripts/fetch_docs.py, the debug listing of the pages an ingest would pick up."""

# [테스트 묶음] scripts/fetch_docs.py(적재 대상 목록을 보여 주는 디버그 명령)의 테스트. GitHub 트리 응답을
# httpx.MockTransport로 흉내 내 네트워크 없이 돈다.
# [왜 중요한가] 한국어 지원으로 list_doc_paths가 언어 인자를 받게 바뀐 뒤 이 스크립트가 옛 호출로 남아 항상
# TypeError로 끝났다. 두 테스트 모두 고치기 전에는 TypeError로 실패했다(커밋 0b0b578).

import httpx
import pytest

from scripts import fetch_docs

# 가짜 GitHub 트리: 영어·한국어 index.md와, 적재에서 빼야 하는 한국어 번역 안내 페이지(translation-banner.md).
TREE = {
    "tree": [
        {"path": "docs/en/docs/index.md", "type": "blob"},
        {"path": "docs/ko/docs/index.md", "type": "blob"},
        {"path": "docs/ko/docs/translation-banner.md", "type": "blob"},
    ]
}


# 이 파일의 모든 테스트에 자동 적용: 스크립트가 만드는 httpx.AsyncClient를 MockTransport가 붙은 클라이언트로
# 바꾼다. 요청 경로가 넘겨준 커밋(deadbeef)의 트리인지도 확인한다(커밋을 주면 최신 커밋 조회를 하지 않으므로
# 요청은 트리 하나뿐이다).
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


# 기본(영어·한국어)으로 두 페이지를 '[언어] 경로' 형식으로 출력하고, 번역 안내 페이지는 빼는지 확인한다.
@pytest.mark.asyncio
async def test_fetch_docs_lists_the_pages_of_every_language(capsys):
    await fetch_docs.main("deadbeef")

    out = capsys.readouterr().out
    assert "doc files found: 2" in out
    assert "[en] docs/en/docs/index.md" in out
    assert "[ko] docs/ko/docs/index.md" in out
    assert "translation-banner.md" not in out


# 언어를 하나(en)만 주면 그 언어의 페이지만 나오는지 확인한다(--languages 옵션).
@pytest.mark.asyncio
async def test_fetch_docs_can_list_one_language(capsys):
    await fetch_docs.main("deadbeef", ("en",))

    out = capsys.readouterr().out
    assert "doc files found: 1" in out
    assert "docs/ko/" not in out

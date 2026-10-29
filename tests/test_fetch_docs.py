"""scripts/fetch_docs.py: 적재가 가져갈 페이지 목록을 보여 주는 디버그 명령의 테스트."""

# [테스트 묶음] scripts/fetch_docs.py(적재 대상 목록을 보여 주는 디버그 명령)의 테스트. GitHub 응답(커밋 조회,
# 트리)을 httpx.MockTransport로 흉내 내 네트워크 없이 돈다.
# [왜 중요한가] 한국어 지원으로 list_doc_paths가 언어 인자를 받게 바뀐 뒤 이 스크립트가 옛 호출로 남아 항상
# TypeError로 끝났다. 처음 두 테스트는 고치기 전에는 TypeError로 실패했다(커밋 0b0b578). 2026-10-29부터는
# ref를 GitHub에 물어 40자 SHA로 바꾸고 기본 ref가 측정 스냅숏이 된 적재 동작(app/services/ingestion.py)을 이
# 명령도 같이 따르는지 본다.

import httpx
import pytest

# 기본 적재 ref를 정하는 설정, 적재 모듈(스냅숏 커밋 상수), 테스트 대상 스크립트.
from app.config import get_settings
from app.services import ingestion
from scripts import fetch_docs

# 가짜 GitHub가 모든 ref에 돌려주는 40자 커밋 SHA.
FULL_SHA = "deadbeef" + "0" * 32

# 가짜 GitHub 트리: 영어·한국어 index.md와, 적재에서 빼야 하는 한국어 번역 안내 페이지(translation-banner.md).
TREE = {
    "tree": [
        {"path": "docs/en/docs/index.md", "type": "blob"},
        {"path": "docs/ko/docs/index.md", "type": "blob"},
        {"path": "docs/ko/docs/translation-banner.md", "type": "blob"},
    ]
}


# 이 파일의 모든 테스트에 자동 적용: 스크립트가 쓰는 GitHub 클라이언트(ingestion.github_client)를
# MockTransport가 붙은 클라이언트로 바꾼다. ref 조회(GET /repos/.../commits/{ref})에는 FULL_SHA를 돌려주고,
# 트리 요청은 그 SHA로 와야 한다(ref 이름으로 트리를 받으면 실패). 조회한 ref는 돌려주는 목록에 차례로 모아
# 테스트가 확인한다.
@pytest.fixture(autouse=True)
def github(monkeypatch):
    refs: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if "/commits/" in path:
            refs.append(path.rsplit("/", 1)[1])
            return httpx.Response(200, json={"sha": FULL_SHA})
        assert path.endswith(f"/git/trees/{FULL_SHA}")
        return httpx.Response(200, json=TREE)

    monkeypatch.setattr(
        fetch_docs, "github_client", lambda: httpx.AsyncClient(transport=httpx.MockTransport(handler))
    )
    return refs


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


# --commit의 ref(여기서는 짧은 SHA)는 적재와 같이 GitHub에 물어 40자 SHA로 바꾸고, 출력에도 그 SHA를 적는다.
@pytest.mark.asyncio
async def test_fetch_docs_resolves_the_ref_through_github(github, capsys):
    await fetch_docs.main("deadbeef")

    assert github == ["deadbeef"]
    assert f"commit: {FULL_SHA}" in capsys.readouterr().out


# --commit이 없고 설정 FASTAPI_DOCS_COMMIT_SHA도 비어 있으면 적재와 같은 기본값인 측정 스냅숏 커밋을 조회한다
# (예전에는 master의 최신 커밋).
@pytest.mark.asyncio
async def test_fetch_docs_defaults_to_the_measured_snapshot(github, monkeypatch):
    settings = get_settings().model_copy(update={"fastapi_docs_commit_sha": ""})
    monkeypatch.setattr(ingestion, "get_settings", lambda: settings)

    await fetch_docs.main(None)

    assert github == [ingestion.DOCS_SNAPSHOT_COMMIT]


# --commit에 안전하지 않은 형식('..' 세그먼트)을 주면 적재 CLI와 같은 사용법 오류(종료 코드 2)다.
def test_fetch_docs_rejects_an_unsafe_ref_option(capsys):
    with pytest.raises(SystemExit) as exc:
        fetch_docs.build_parser().parse_args(["--commit", "a..b"])

    assert exc.value.code == 2
    assert "usage:" in capsys.readouterr().err

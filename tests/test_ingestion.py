"""재적재가 코퍼스를 상류 문서 트리와 맞게 유지하는지 검증한다.

바뀌지 않은 페이지는 건너뛰고, 바뀐 페이지는 청크를 교체하며, 전체 실행은 목록에 더는 없는 페이지를
지운다. 그래서 이름이 바뀌거나 지워진 문서 페이지가 계속 검색·인용될 수 없다. GitHub 호출은 메모리 속
트리로 바꾼다.
"""

# [테스트 묶음] 재적재(app/services/ingestion.py의 run_ingestion)가 DB의 문서를 GitHub 문서 트리와 맞게
# 유지하는지 확인하는 통합 테스트. 실제 테스트 DB를 쓰고, GitHub 호출 세 개(커밋, 목록, 원문)는 메모리 속 가짜
# 트리로 바꾼다. 뒷부분(2026-10-29)은 ref → 40자 SHA 해석, limit 범위, 동시 적재 잠금을 본다.
# [왜 중요한가] 전체 적재가 트리에서 사라진 문서를 지우지 않으면, 이름이 바뀌거나 지워진 페이지가 계속
# 검색되고 없는 페이지로 인용된다. 반대로 지우는 범위가 넓으면 아직 있는 페이지까지 지운다. 그래서 '언제
# 지우고 언제 지우지 않는가'의 경계(limit, dry run, 다른 언어, 빈 목록, 잘린 목록)를 하나씩 고정한다(커밋
# ff32ead).
# [import] asyncio는 두 적재를 실제로 겹쳐 돌리는 데, httpx는 GitHub 응답을 MockTransport로 흉내 내는 데(잘린
# 트리, ref 해석), SQLAlchemy는 저장된 문서·청크를 직접 세는 조회와 다른 세션에서 적재 잠금을 쥐는 SQL에 쓴다.

import asyncio

import httpx
import pytest
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import async_sessionmaker

# 기본 적재 ref를 정하는 설정, DB를 직접 조회할 문서·청크 모델, 테스트 대상 적재 모듈, 결정론적 가짜 임베딩.
from app.config import get_settings
from app.models.chunk import Chunk
from app.models.document import Document
from app.services import ingestion
from tests.conftest import FakeEmbeddingService

# 가짜 트리의 페이지: 영어 두 개(A, B), 한국어 하나(C), 적재에서 빼야 하는 번역 안내 페이지(BANNER).
A = "docs/en/docs/a.md"
B = "docs/en/docs/b.md"
C = "docs/ko/docs/c.md"
BANNER = "docs/en/docs/translation-banner.md"

PAGES = {
    A: "# A\n\nPath parameters are declared in the path string.\n",
    B: "# B\n\nQuery parameters come after the question mark.\n",
    C: "# C\n\n경로 매개변수는 경로 문자열에 선언합니다.\n",
}


# 적재가 `pages`를 커밋 deadbeef의 문서 트리로 보게 만든다. 목록은 실제 select_doc_paths로 골라 언어 필터와
# 제외 페이지 규칙은 진짜 코드가 적용한다. 테스트 중간에 다시 불러 '상류 트리가 바뀐 상황'을 만든다.
def serve_upstream(monkeypatch, pages: dict[str, str]) -> None:
    """적재가 `pages`를 커밋 deadbeef의 문서 트리로 보게 한다."""

    async def fake_commit_sha(client, commit_sha=None):
        return "deadbeef"

    async def fake_doc_paths(client, sha, languages):
        tree = [{"path": path, "type": "blob"} for path in pages]
        return ingestion.select_doc_paths(tree, languages)

    async def fake_raw_file(client, sha, path):
        return pages[path]

    monkeypatch.setattr(ingestion, "resolve_commit_sha", fake_commit_sha)
    monkeypatch.setattr(ingestion, "list_doc_paths", fake_doc_paths)
    monkeypatch.setattr(ingestion, "fetch_raw_file", fake_raw_file)


# 모든 언어에 가짜 임베딩을 쓰는 적재 한 번. kwargs로 languages, limit, dry_run을 넘긴다.
async def ingest(db, **kwargs):
    return await ingestion.run_ingestion(db, lambda language: FakeEmbeddingService(), **kwargs)


# DB에 남아 있는 문서 경로 집합, 그리고 경로로 문서 id를 찾는 도우미.
async def stored_paths(db) -> set[str]:
    return set(await db.scalars(select(Document.source_path)))


async def document_id(db, path: str):
    return await db.scalar(select(Document.id).where(Document.source_path == path))


# 내용이 같은 문서를 다시 적재하면 해시가 같아 모두 건너뛴다(처리 0, 건너뜀 3, 삭제 0). 결과 필드 이름은
# chunks_skipped지만 세는 것은 건너뛴 문서 수다.
@pytest.mark.asyncio
async def test_rerunning_unchanged_docs_skips_them(db_session, monkeypatch):
    serve_upstream(monkeypatch, PAGES)
    await ingest(db_session)

    outcome = await ingest(db_session)

    assert outcome.documents_processed == 0
    assert outcome.chunks_skipped == len(PAGES)
    assert outcome.documents_deleted == 0


# 영어만 적재한 전체 실행에서 트리에서 사라진 영어 페이지 B는 지워지고 그 청크도 함께 사라지며(외래 키 ON
# DELETE CASCADE), 이번에 적재하지 않은 언어(한국어 C)는 그대로 남는지 확인한다.
@pytest.mark.asyncio
async def test_a_full_run_removes_pages_that_left_the_upstream_tree(db_session, monkeypatch):
    serve_upstream(monkeypatch, PAGES)
    await ingest(db_session)
    b_id = await document_id(db_session, B)

    serve_upstream(monkeypatch, {A: PAGES[A]})
    outcome = await ingest(db_session, languages=("en",))

    # 한국어 페이지는 이번 실행이 적재한 언어 밖이므로 남는다.
    assert await stored_paths(db_session) == {A, C}
    assert outcome.documents_deleted == 1
    orphaned = await db_session.scalar(
        select(func.count()).select_from(Chunk).where(Chunk.document_id == b_id)
    )
    assert orphaned == 0


# 트리에는 있지만 제외 대상이 된 페이지(translation-banner.md가 SKIPPED_PAGES에 들어가기 전에 적재된 행)도
# 지운다. 목록에서 빠졌으므로 '트리에 없는 문서'와 같이 취급된다.
@pytest.mark.asyncio
async def test_a_page_that_became_excluded_is_removed(db_session, monkeypatch):
    # translation-banner.md가 SKIPPED_PAGES에 들어가기 전에 적재된 행.
    db_session.add(
        Document(source_path=BANNER, title="Banner", source_commit_sha="old", content_hash="old")
    )
    await db_session.commit()

    serve_upstream(monkeypatch, {**PAGES, BANNER: "# Banner\n"})
    outcome = await ingest(db_session)

    assert await stored_paths(db_session) == set(PAGES)
    assert outcome.documents_deleted == 1


# --limit을 준 실행은 트리의 일부만 보므로 아무것도 지우지 않아야 한다.
@pytest.mark.asyncio
async def test_a_limited_run_deletes_nothing(db_session, monkeypatch):
    serve_upstream(monkeypatch, PAGES)
    await ingest(db_session)

    serve_upstream(monkeypatch, {A: PAGES[A], C: PAGES[C]})
    outcome = await ingest(db_session, limit=1)

    assert outcome.documents_deleted == 0
    assert await stored_paths(db_session) == set(PAGES)


# dry run은 지울 문서 수(B 하나)만 세고 실제로는 지우지 않는다.
@pytest.mark.asyncio
async def test_a_dry_run_counts_stale_pages_without_deleting_them(db_session, monkeypatch):
    serve_upstream(monkeypatch, PAGES)
    await ingest(db_session)

    serve_upstream(monkeypatch, {A: PAGES[A], C: PAGES[C]})
    outcome = await ingest(db_session, dry_run=True)

    assert outcome.documents_deleted == 1
    assert await stored_paths(db_session) == set(PAGES)


# 어떤 언어의 목록이 비어 있으면(여기서는 한국어) 그 언어 문서는 건드리지 않는다. 빈 목록은 모든 페이지가
# 지워졌다기보다 상류 구조 변경이나 잘못된 언어 코드일 가능성이 크기 때문이다.
@pytest.mark.asyncio
async def test_a_language_that_lists_no_pages_is_left_alone(db_session, monkeypatch):
    serve_upstream(monkeypatch, PAGES)
    await ingest(db_session)

    serve_upstream(monkeypatch, {A: PAGES[A], B: PAGES[B]})
    outcome = await ingest(db_session)

    assert outcome.documents_deleted == 0
    assert await stored_paths(db_session) == set(PAGES)


# 내용이 바뀐 문서는 다시 처리되고 fetched_at이 새 시각으로 바뀌어야 한다(커밋 ff32ead). 첫 적재 뒤
# commit으로 트랜잭션을 끝내는 이유: PostgreSQL의 now()는 트랜잭션 시작 시각이라, 같은 트랜잭션이면 두 값이
# 같아진다.
@pytest.mark.asyncio
async def test_an_updated_page_gets_a_new_fetched_at(db_session, monkeypatch):
    serve_upstream(monkeypatch, PAGES)
    await ingest(db_session)
    first = await db_session.scalar(select(Document.fetched_at).where(Document.source_path == A))
    await db_session.commit()

    serve_upstream(monkeypatch, {**PAGES, A: PAGES[A] + "\nThey are converted to the declared type.\n"})
    outcome = await ingest(db_session)

    assert outcome.documents_processed == 1
    second = await db_session.scalar(select(Document.fetched_at).where(Document.source_path == A))
    assert second > first


# GitHub가 트리 목록이 잘렸다(truncated)고 알려 주면 목록 함수가 RuntimeError로 거부해야 한다. 일부만 담긴
# 목록으로 전체 실행을 하면 아직 있는 페이지를 지우게 된다. 여기서는 MockTransport로 GitHub 응답 자체를 흉내
# 낸다.
@pytest.mark.asyncio
async def test_a_truncated_tree_listing_is_refused():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"tree": [{"path": A, "type": "blob"}], "truncated": True})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(RuntimeError, match="truncated"):
            await ingestion.list_doc_paths(client, "deadbeef", ("en",))


# 같은 모델 이름에 다른 고정 리비전을 가진 가짜 임베딩. identity에 '@리비전'이 붙어 적재 해시가 달라진다.
class RevisedEmbeddingService(FakeEmbeddingService):
    """같은 모델 이름, 다른 고정 리비전: 이름은 같지만 벡터가 다르다."""

    revision = "0" * 40


# 원문이 그대로여도 임베딩 모델의 리비전이 바뀌면 모든 문서를 다시 임베딩해야 한다. 해시에 모델 identity가
# 들어가지 않으면 다른 모델의 벡터가 '변경 없음'으로 남는다(README 설계 판단 '청커 버전을 수집 해시에 포함').
@pytest.mark.asyncio
async def test_a_new_model_revision_reembeds_unchanged_pages(db_session, monkeypatch):
    serve_upstream(monkeypatch, PAGES)
    await ingest(db_session)

    outcome = await ingestion.run_ingestion(db_session, lambda language: RevisedEmbeddingService())

    assert outcome.documents_processed == len(PAGES)
    assert outcome.chunks_skipped == 0


# --- 커밋 ref 해석 (resolve_commit_sha, 2026-10-29) ---
# 아래 테스트는 serve_upstream과 달리 적재 함수를 바꾸지 않고 GitHub API·raw 호스트의 HTTP 응답만
# httpx.MockTransport로 흉내 낸다. 그래서 ref → 40자 SHA 해석과 URL 구성까지 실제 코드가 돈다.

# 가짜 GitHub가 아는 모든 ref에 돌려주는 40자 커밋 SHA.
FULL_SHA = "c0ffee" + "0" * 34


# GitHub를 통째로 흉내 내는 클라이언트를 ingestion.github_client 자리에 끼운다.
# - GET /repos/{REPO}/commits/{ref}: ref가 known_refs에 있으면 {"sha": FULL_SHA}, 아니면 404.
# - GET /repos/{REPO}/git/trees/{FULL_SHA}: pages의 경로를 blob으로 담은 트리.
# - GET raw.githubusercontent.com/{REPO}/{FULL_SHA}/{path}: pages[path]의 원문.
# 그 밖의 요청은 404. 요청한 URL은 돌려주는 목록에 차례로 모아 테스트가 확인한다.
def serve_github(monkeypatch, pages: dict[str, str], known_refs: set[str]) -> list[str]:
    requests: list[str] = []
    commits_prefix = f"/repos/{ingestion.REPO}/commits/"
    tree_path = f"/repos/{ingestion.REPO}/git/trees/{FULL_SHA}"
    raw_prefix = f"/{ingestion.REPO}/{FULL_SHA}/"

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(str(request.url))
        path = request.url.path
        if request.url.host == "api.github.com" and path.startswith(commits_prefix):
            ref = path[len(commits_prefix) :]
            if ref in known_refs:
                return httpx.Response(200, json={"sha": FULL_SHA})
            return httpx.Response(404, json={"message": f"No commit found for SHA: {ref}"})
        if request.url.host == "api.github.com" and path == tree_path:
            tree = [{"path": page, "type": "blob"} for page in pages]
            return httpx.Response(200, json={"tree": tree, "truncated": False})
        if request.url.host == "raw.githubusercontent.com" and path.startswith(raw_prefix):
            return httpx.Response(200, text=pages[path[len(raw_prefix) :]])
        return httpx.Response(404, text="not found")

    monkeypatch.setattr(
        ingestion, "github_client", lambda: httpx.AsyncClient(transport=httpx.MockTransport(handler))
    )
    return requests


# 측정에 쓴 문서 스냅숏 커밋은 docs/experiments.md의 재적재 명령들이 적는 값과 같아야 한다(조용히 바뀌지
# 않게).
def test_the_snapshot_commit_is_the_measured_one():
    assert ingestion.DOCS_SNAPSHOT_COMMIT == "50113da16fec53b66b80d75e80a89296de4fa5a5"


# commit_sha로 브랜치 이름·짧은 SHA·40자 SHA 어느 것을 줘도 적재는 GitHub의 commits API가 돌려준 40자 SHA로
# 트리·원문을 받고 그 SHA를 모든 문서 행의 source_commit_sha에 저장해야 한다. 예전에는 값이 있으면 조회 없이
# 그대로 써서 'master'가 문서 행에 저장돼 어느 커밋의 문서인지 기록이 남지 않았다(측정 재현의 근거가 사라짐).
@pytest.mark.asyncio
@pytest.mark.parametrize("ref", ["master", FULL_SHA[:7], FULL_SHA])
async def test_any_ref_is_stored_as_the_sha_github_resolves_it_to(db_session, monkeypatch, ref):
    requests = serve_github(monkeypatch, PAGES, known_refs={ref})

    outcome = await ingest(db_session, commit_sha=ref)

    assert outcome.commit_sha == FULL_SHA
    assert outcome.documents_processed == len(PAGES)
    assert set(await db_session.scalars(select(Document.source_commit_sha))) == {FULL_SHA}
    assert requests[0] == f"{ingestion.GITHUB_API}/repos/{ingestion.REPO}/commits/{ref}"
    # 트리와 원문은 입력한 ref가 아니라 해석된 SHA로 받는다.
    assert len(requests) == 1 + 1 + len(PAGES)
    assert all(FULL_SHA in url for url in requests[1:])


# commit_sha를 주지 않으면 설정 FASTAPI_DOCS_COMMIT_SHA의 ref를, 그것도 비어 있으면 측정에 쓴 문서
# 스냅숏(DOCS_SNAPSHOT_COMMIT)을 GitHub에 묻는다. 예전 기본값은 master의 최신 커밋이어서 README를 그대로 따라
# 한 적재가 측정과 다른 코퍼스가 됐다. 최신 문서는 설정이나 --commit에 master를 명시해 받는다.
@pytest.mark.asyncio
@pytest.mark.parametrize("configured", ["", "  ", "master"])
async def test_the_default_ref_is_the_configured_one_or_the_snapshot(db_session, monkeypatch, configured):
    expected = configured.strip() or ingestion.DOCS_SNAPSHOT_COMMIT
    settings = get_settings().model_copy(update={"fastapi_docs_commit_sha": configured})
    monkeypatch.setattr(ingestion, "get_settings", lambda: settings)
    requests = serve_github(monkeypatch, PAGES, known_refs={expected})

    outcome = await ingest(db_session)

    assert outcome.commit_sha == FULL_SHA
    assert requests[0] == f"{ingestion.GITHUB_API}/repos/{ingestion.REPO}/commits/{expected}"


# 설정 FASTAPI_DOCS_COMMIT_SHA가 안전하지 않은 형식이면 GitHub에 묻기 전에 설정 이름을 담은 ValueError로
# 끝난다.
@pytest.mark.asyncio
async def test_an_unsafe_configured_ref_is_rejected_before_any_request(monkeypatch):
    settings = get_settings().model_copy(update={"fastapi_docs_commit_sha": "../x"})
    monkeypatch.setattr(ingestion, "get_settings", lambda: settings)
    requests = serve_github(monkeypatch, PAGES, known_refs=set())

    async with ingestion.github_client() as client:
        with pytest.raises(ValueError, match="FASTAPI_DOCS_COMMIT_SHA"):
            await ingestion.resolve_commit_sha(client)

    assert requests == []


# 형식이 안전하지 않은 ref는 GitHub에 묻지도 않고 ValueError다. 값은 GitHub URL 경로에 그대로 들어가므로
# '..'·'.' 세그먼트는 다른 API 경로를 가리키고(httpx가 점 세그먼트를 정규화해, 예를 들어 '.' 하나는 커밋
# 하나가 아니라 커밋 목록 경로 .../commits를 요청한다), 공백·'?'·'#'은 경로를 끊으며, 100자가 넘는 값은 실제
# ref가 아니다. 이 검사는 보안 통제가 아니라 정확성 검사다(app/services/ingestion.py 주석).
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "ref",
    [
        "a..b",
        "../x",
        ".",
        "./x",
        "a/./b",
        "x/.",
        ".hidden",
        "x?y",
        "x#y",
        "x y",
        "a" * 101,
        "/master",
        "master/",
        "a//b",
        "",
    ],
)
async def test_an_unsafe_ref_is_rejected_before_any_github_request(monkeypatch, ref):
    requests = serve_github(monkeypatch, PAGES, known_refs=set())

    async with ingestion.github_client() as client:
        with pytest.raises(ValueError):
            await ingestion.resolve_commit_sha(client, ref)

    assert requests == []


# GitHub가 모르는 ref(없는 브랜치, 오타 난 SHA)는 commits 조회의 404가 그대로 올라와 트리·원문을 하나도 받지
# 않고 끝난다. 예전에는 40자가 아닌 값이 트리 조회에서 404로, 트리 조회를 통과한 긴 값은 문서 행을 flush할 때
# DataError로 끝났다.
@pytest.mark.asyncio
async def test_a_ref_github_does_not_know_fails_before_any_download(monkeypatch):
    requests = serve_github(monkeypatch, PAGES, known_refs=set())

    async with ingestion.github_client() as client:
        with pytest.raises(httpx.HTTPStatusError):
            await ingestion.resolve_commit_sha(client, "no-such-branch")

    assert len(requests) == 1


# commits 응답의 sha가 40자 16진수가 아니면 RuntimeError. 저장 열 source_commit_sha(String(40))과 URL이 그
# 형식을 가정하므로, 뜻밖의 응답으로 적재를 이어 가지 않는다.
@pytest.mark.asyncio
async def test_an_unexpected_commit_response_is_refused():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"sha": "master"})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(RuntimeError, match="commit sha"):
            await ingestion.resolve_commit_sha(client, "master")


# commits 응답이 커밋 하나(JSON 객체)가 아니라 목록(JSON 배열)이어도 AttributeError가 아니라 같은
# RuntimeError로 끝나야 한다. GitHub는 commits/{ref} 아래에 목록을 돌려주는 하위 경로(예: {ref}/statuses,
# {ref}/pulls)도 두므로, 형식 검사를 통과한 ref가 그런 경로에 닿을 수 있다.
@pytest.mark.asyncio
async def test_a_commit_listing_response_is_refused():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=[{"sha": FULL_SHA}])

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(RuntimeError, match="commit sha"):
            await ingestion.resolve_commit_sha(client, "master/statuses")


# --- limit 범위 ---


# limit 0·음수는 적재 함수에서도 ValueError다(API는 422로 먼저 막고, CLI는 사용법 오류). 예전에는 참·거짓
# 판정이라 0이 '전체 적재 + 삭제', 음수가 paths[:-n]이었다. GitHub에 닿기 전에 거부하는지 함께 본다.
@pytest.mark.asyncio
@pytest.mark.parametrize("limit", [0, -1])
async def test_a_limit_below_one_is_rejected_before_any_work(db_session, monkeypatch, limit):
    serve_upstream(monkeypatch, PAGES)

    def must_not_connect():
        raise AssertionError("GitHub was contacted")

    monkeypatch.setattr(ingestion, "github_client", must_not_connect, raising=False)

    with pytest.raises(ValueError, match="limit"):
        await ingest(db_session, limit=limit)


# --- 동시 적재 잠금 (pg_try_advisory_xact_lock) ---


# 다른 세션에서 적재 잠금을 쥔다(트랜잭션이 끝날 때까지 유지). 관리자 API의 다른 요청이나 다른 프로세스(CLI)가
# 적재 중인 상황을 흉내 낸다.
async def hold_ingestion_lock(session) -> None:
    await session.execute(
        text("SELECT pg_advisory_xact_lock(CAST(:key AS bigint))"), {"key": ingestion.INGESTION_LOCK_KEY}
    )


# 다른 세션이 잠금을 쥔 동안 두 번째 run_ingestion은 GitHub에 묻기 전에 바로 IngestionAlreadyRunning으로
# 끝나고, 그 세션이 트랜잭션을 끝내면 다시 적재할 수 있어야 한다. 예전에는 잠금이 없어 두 적재가 함께 돌았고,
# 늦은 쪽이 먼저 쪽의 commit을 몇 분 기다린 뒤 유일 제약 위반 500으로 끝났다(app/services/ingestion.py의
# _acquire_ingestion_lock 주석).
@pytest.mark.asyncio
async def test_a_second_ingestion_is_refused_while_another_holds_the_lock(db_engine, db_session, monkeypatch):
    serve_upstream(monkeypatch, PAGES)

    def must_not_connect():
        raise AssertionError("GitHub was contacted while the lock was held")

    monkeypatch.setattr(ingestion, "github_client", must_not_connect, raising=False)
    other = async_sessionmaker(db_engine)()
    try:
        await hold_ingestion_lock(other)
        with pytest.raises(ingestion.IngestionAlreadyRunning):
            await ingest(db_session)
    finally:
        await other.rollback()
        await other.close()

    monkeypatch.setattr(ingestion, "github_client", httpx.AsyncClient)
    outcome = await ingest(db_session)
    assert outcome.documents_processed == len(PAGES)


# 실제로 겹친 두 적재: 첫 적재가 원문을 받는 동안(잠금을 쥔 채 GitHub를 기다리는 중) 다른 세션에서 시작한 두
# 번째 적재는 기다리지 않고 바로 IngestionAlreadyRunning이고, 첫 적재는 그대로 끝나야 한다. 잠금을 네트워크
# 단계 앞에서 잡아 트랜잭션 끝까지 쥐는지를 실제 run_ingestion 두 개로 본다(관리자 API와 CLI가 겹친 상황).
# 고치기 전 코드에는 잠금이 없어 두 번째 적재도 그대로 원문 받기까지 들어갔다. 이렇게 짧은 가짜 적재에서는
# 시점에 따라 늦은 쪽이 먼저 끝난 쪽의 commit된 문서를 보고 건너뛰어 둘 다 성공하기도 하지만, 실제 적재처럼 첫
# 트랜잭션이 몇 분 열려 있으면 늦은 쪽은 같은 문서를 쓰려다 먼저 쪽의 commit을 기다린 뒤 유일 제약 위반으로
# 끝난다.
@pytest.mark.asyncio
async def test_overlapping_ingestions_run_one_at_a_time(db_engine, db_session, monkeypatch):
    serve_upstream(monkeypatch, PAGES)
    fetching = asyncio.Event()
    release = asyncio.Event()
    serve_raw_file = ingestion.fetch_raw_file

    # 첫 적재의 원문 받기를 release가 켜질 때까지 붙잡아, 첫 적재가 일하는 도중에 두 번째 적재를 시작한다.
    async def gated_raw_file(client, sha, path):
        fetching.set()
        await release.wait()
        return await serve_raw_file(client, sha, path)

    monkeypatch.setattr(ingestion, "fetch_raw_file", gated_raw_file)
    first = asyncio.create_task(ingest(db_session))
    other = async_sessionmaker(db_engine, expire_on_commit=False)()
    try:
        await asyncio.wait_for(fetching.wait(), timeout=10)
        with pytest.raises(ingestion.IngestionAlreadyRunning):
            await asyncio.wait_for(ingest(other), timeout=10)
    finally:
        release.set()
        outcome = await first
        await other.rollback()
        await other.close()

    assert outcome.documents_processed == len(PAGES)
    assert await stored_paths(db_session) == set(PAGES)


# dry run은 DB를 쓰지 않으므로 잠금을 잡지 않는다. 다른 적재가 돌고 있어도 처리·삭제될 개수를 셀 수 있다.
@pytest.mark.asyncio
async def test_a_dry_run_does_not_need_the_lock(db_engine, db_session, monkeypatch):
    serve_upstream(monkeypatch, PAGES)
    other = async_sessionmaker(db_engine)()
    try:
        await hold_ingestion_lock(other)
        outcome = await ingest(db_session, dry_run=True)
    finally:
        await other.rollback()
        await other.close()

    assert outcome.documents_processed == len(PAGES)


# 적재가 commit으로 끝나면 트랜잭션 잠금도 풀려 다른 세션이 바로 잠금을 잡을 수 있다(같은 세션의 재적재는 위
# test_rerunning_unchanged_docs_skips_them이 함께 보여 준다).
@pytest.mark.asyncio
async def test_the_lock_is_released_when_the_run_commits(db_engine, db_session, monkeypatch):
    serve_upstream(monkeypatch, PAGES)
    await ingest(db_session)

    other = async_sessionmaker(db_engine)()
    try:
        locked = await other.scalar(
            text("SELECT pg_try_advisory_xact_lock(CAST(:key AS bigint))"),
            {"key": ingestion.INGESTION_LOCK_KEY},
        )
    finally:
        await other.rollback()
        await other.close()

    assert locked is True

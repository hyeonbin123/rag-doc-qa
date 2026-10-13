"""Re-ingestion keeps the corpus in step with the upstream docs tree.

Unchanged pages are skipped, changed pages have their chunks replaced, and a full run
removes pages that are no longer listed, so a renamed or deleted docs page can't stay
searchable and citable. The GitHub calls are replaced with an in-memory tree.
"""

# [테스트 묶음] 재적재(app/services/ingestion.py의 run_ingestion)가 DB의 문서를 GitHub 문서 트리와 맞게
# 유지하는지 확인하는 통합 테스트. 실제 테스트 DB를 쓰고, GitHub 호출 세 개(커밋, 목록, 원문)는 메모리 속 가짜
# 트리로 바꾼다.
# [왜 중요한가] 전체 적재가 트리에서 사라진 문서를 지우지 않으면, 이름이 바뀌거나 지워진 페이지가 계속
# 검색되고 없는 페이지로 인용된다. 반대로 지우는 범위가 넓으면 아직 있는 페이지까지 지운다. 그래서 '언제
# 지우고 언제 지우지 않는가'의 경계(limit, dry run, 다른 언어, 빈 목록, 잘린 목록)를 하나씩 고정한다(커밋
# ff32ead).
# [import] httpx는 잘린 트리 테스트에서 GitHub 응답을 MockTransport로 흉내 내는 데, SQLAlchemy는 저장된
# 문서·청크를 직접 세는 조회에 쓴다.

import httpx
import pytest
from sqlalchemy import func, select

# DB를 직접 조회할 문서·청크 모델, 테스트 대상 적재 모듈, 결정론적 가짜 임베딩.
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
    """Make the ingestion see `pages` as the docs tree at commit deadbeef."""

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

    # The Korean page is outside the languages this run ingested, so it stays.
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
    # Ingested before translation-banner.md joined SKIPPED_PAGES.
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
    # An empty listing for a translation more likely means an upstream restructure or
    # a wrong language code than that every page was deleted.
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
    # A partial listing would make a full run delete pages that still exist.
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"tree": [{"path": A, "type": "blob"}], "truncated": True})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(RuntimeError, match="truncated"):
            await ingestion.list_doc_paths(client, "deadbeef", ("en",))


# 같은 모델 이름에 다른 고정 리비전을 가진 가짜 임베딩. identity에 '@리비전'이 붙어 적재 해시가 달라진다.
class RevisedEmbeddingService(FakeEmbeddingService):
    """The same model name at another pinned revision: different vectors, same name."""

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

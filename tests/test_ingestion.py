"""Re-ingestion keeps the corpus in step with the upstream docs tree.

Unchanged pages are skipped, changed pages have their chunks replaced, and a full run
removes pages that are no longer listed, so a renamed or deleted docs page can't stay
searchable and citable. The GitHub calls are replaced with an in-memory tree.
"""

import httpx
import pytest
from sqlalchemy import func, select

from app.models.chunk import Chunk
from app.models.document import Document
from app.services import ingestion
from tests.conftest import FakeEmbeddingService

A = "docs/en/docs/a.md"
B = "docs/en/docs/b.md"
C = "docs/ko/docs/c.md"
BANNER = "docs/en/docs/translation-banner.md"

PAGES = {
    A: "# A\n\nPath parameters are declared in the path string.\n",
    B: "# B\n\nQuery parameters come after the question mark.\n",
    C: "# C\n\n경로 매개변수는 경로 문자열에 선언합니다.\n",
}


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


async def ingest(db, **kwargs):
    return await ingestion.run_ingestion(db, lambda language: FakeEmbeddingService(), **kwargs)


async def stored_paths(db) -> set[str]:
    return set(await db.scalars(select(Document.source_path)))


async def document_id(db, path: str):
    return await db.scalar(select(Document.id).where(Document.source_path == path))


@pytest.mark.asyncio
async def test_rerunning_unchanged_docs_skips_them(db_session, monkeypatch):
    serve_upstream(monkeypatch, PAGES)
    await ingest(db_session)

    outcome = await ingest(db_session)

    assert outcome.documents_processed == 0
    assert outcome.chunks_skipped == len(PAGES)
    assert outcome.documents_deleted == 0


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


@pytest.mark.asyncio
async def test_a_limited_run_deletes_nothing(db_session, monkeypatch):
    serve_upstream(monkeypatch, PAGES)
    await ingest(db_session)

    serve_upstream(monkeypatch, {A: PAGES[A], C: PAGES[C]})
    outcome = await ingest(db_session, limit=1)

    assert outcome.documents_deleted == 0
    assert await stored_paths(db_session) == set(PAGES)


@pytest.mark.asyncio
async def test_a_dry_run_counts_stale_pages_without_deleting_them(db_session, monkeypatch):
    serve_upstream(monkeypatch, PAGES)
    await ingest(db_session)

    serve_upstream(monkeypatch, {A: PAGES[A], C: PAGES[C]})
    outcome = await ingest(db_session, dry_run=True)

    assert outcome.documents_deleted == 1
    assert await stored_paths(db_session) == set(PAGES)


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


@pytest.mark.asyncio
async def test_a_truncated_tree_listing_is_refused():
    # A partial listing would make a full run delete pages that still exist.
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"tree": [{"path": A, "type": "blob"}], "truncated": True})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(RuntimeError, match="truncated"):
            await ingestion.list_doc_paths(client, "deadbeef", ("en",))


class RevisedEmbeddingService(FakeEmbeddingService):
    """The same model name at another pinned revision: different vectors, same name."""

    revision = "0" * 40


@pytest.mark.asyncio
async def test_a_new_model_revision_reembeds_unchanged_pages(db_session, monkeypatch):
    serve_upstream(monkeypatch, PAGES)
    await ingest(db_session)

    outcome = await ingestion.run_ingestion(db_session, lambda language: RevisedEmbeddingService())

    assert outcome.documents_processed == len(PAGES)
    assert outcome.chunks_skipped == 0

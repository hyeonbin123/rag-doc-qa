"""Fetch the FastAPI docs from GitHub, chunk them, embed them, and upsert into Postgres.

Idempotent by content hash: unchanged files are skipped, changed files have
their chunks fully replaced, so re-running ingestion after a doc update only
recomputes what actually changed.
"""

from __future__ import annotations

import asyncio
import hashlib
import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass

import httpx
from sqlalchemy import delete, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chunk import Chunk
from app.models.document import Document
from app.services.chunking import (
    CHUNKER_VERSION,
    build_embedding_text,
    chunk_markdown,
    strip_heading_anchor,
)
from app.services.embedding import EmbeddingService
from app.services.language import SUPPORTED_LANGUAGES

GITHUB_API = "https://api.github.com"
RAW_BASE = "https://raw.githubusercontent.com"
REPO = "tiangolo/fastapi"
DOC_LANGUAGES: tuple[str, ...] = SUPPORTED_LANGUAGES
# Site furniture rather than documentation: the notice MkDocs puts on AI-assisted
# translations.
SKIPPED_PAGES = {"translation-banner.md"}
MAX_CONCURRENT_FETCHES = 8


def docs_prefix(language: str) -> str:
    return f"docs/{language}/docs/"


def select_doc_paths(tree: list[dict], languages: Sequence[str]) -> list[tuple[str, str]]:
    """(path, language) for every Markdown page of the requested translations."""
    selected = []
    for item in tree:
        path = item["path"]
        if item["type"] != "blob" or not path.endswith(".md"):
            continue
        for language in languages:
            prefix = docs_prefix(language)
            if path.startswith(prefix) and path[len(prefix):] not in SKIPPED_PAGES:
                selected.append((path, language))
                break
    return selected


async def resolve_commit_sha(client: httpx.AsyncClient, commit_sha: str | None = None) -> str:
    if commit_sha:
        return commit_sha
    resp = await client.get(f"{GITHUB_API}/repos/{REPO}/commits/master")
    resp.raise_for_status()
    return resp.json()["sha"]


async def list_doc_paths(
    client: httpx.AsyncClient, sha: str, languages: Sequence[str]
) -> list[tuple[str, str]]:
    resp = await client.get(f"{GITHUB_API}/repos/{REPO}/git/trees/{sha}", params={"recursive": "1"})
    resp.raise_for_status()
    return select_doc_paths(resp.json()["tree"], languages)


async def fetch_raw_file(client: httpx.AsyncClient, sha: str, path: str) -> str:
    resp = await client.get(f"{RAW_BASE}/{REPO}/{sha}/{path}")
    resp.raise_for_status()
    return resp.text


def extract_title(raw_text: str, fallback: str) -> str:
    for line in raw_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return strip_heading_anchor(stripped[2:].strip())
    return fallback


async def _vacuum_chunks(db: AsyncSession) -> None:
    """Clear the rows that replaced chunks leave behind.

    A changed doc has its chunks deleted and reinserted. Until vacuum removes the dead
    rows, HNSW scans still walk them and spend their ef_search budget on rows they
    then discard. That is the likeliest cause of an English dev-set hit that went
    missing right after a bulk re-ingest and came back once autovacuum had run.
    VACUUM can't run inside a transaction, hence the autocommit connection.
    """
    async with db.bind.connect() as conn:
        conn = await conn.execution_options(isolation_level="AUTOCOMMIT")
        await conn.execute(text("VACUUM (ANALYZE) chunks"))


@dataclass
class IngestOutcome:
    documents_processed: int
    chunks_created: int
    chunks_updated: int
    chunks_skipped: int
    elapsed_ms: int
    commit_sha: str


async def run_ingestion(
    db: AsyncSession,
    embedder_for: Callable[[str], EmbeddingService],
    commit_sha: str | None = None,
    limit: int | None = None,
    dry_run: bool = False,
    languages: Sequence[str] = DOC_LANGUAGES,
) -> IngestOutcome:
    start = time.perf_counter()
    documents_processed = 0
    chunks_created = 0
    chunks_updated = 0
    chunks_skipped = 0

    async with httpx.AsyncClient(
        timeout=30.0, headers={"User-Agent": "rag-doc-qa-ingest"}, follow_redirects=True
    ) as client:
        sha = await resolve_commit_sha(client, commit_sha)
        paths = await list_doc_paths(client, sha, languages)
        if limit:
            paths = paths[:limit]

        semaphore = asyncio.Semaphore(MAX_CONCURRENT_FETCHES)

        async def fetch(path: str, language: str) -> tuple[str, str, str]:
            async with semaphore:
                return path, language, await fetch_raw_file(client, sha, path)

        results = await asyncio.gather(*(fetch(p, lang) for p, lang in paths))

    for path, language, raw_text in results:
        embedder = embedder_for(language)
        # The chunker version and the embedding model are part of the key: otherwise
        # changing either would leave every unchanged doc "skipped" and silently keep
        # its stale chunks, or vectors from a different model.
        content_hash = hashlib.sha256(
            f"chunker-v{CHUNKER_VERSION}\nembedding-{embedder.model_name}\n{raw_text}".encode()
        ).hexdigest()

        existing = await db.scalar(select(Document).where(Document.source_path == path))

        if existing is not None and existing.content_hash == content_hash:
            chunks_skipped += 1
            continue

        title = extract_title(raw_text, fallback=path)
        chunk_results = chunk_markdown(raw_text)

        if dry_run:
            documents_processed += 1
            if existing is not None:
                chunks_updated += len(chunk_results)
            else:
                chunks_created += len(chunk_results)
            continue

        if existing is not None:
            await db.execute(delete(Chunk).where(Chunk.document_id == existing.id))
            existing.content_hash = content_hash
            existing.title = title
            existing.source_commit_sha = sha
            document = existing
            chunks_updated += len(chunk_results)
        else:
            document = Document(
                source_path=path,
                title=title,
                source_commit_sha=sha,
                content_hash=content_hash,
            )
            db.add(document)
            await db.flush()
            chunks_created += len(chunk_results)

        if chunk_results:
            embedding_texts = [
                build_embedding_text(c.heading_path, c.content) for c in chunk_results
            ]
            embeddings = embedder.embed_passages(embedding_texts)

            paired = zip(chunk_results, embeddings, strict=True)
            for idx, (chunk_result, embedding) in enumerate(paired):
                db.add(
                    Chunk(
                        document_id=document.id,
                        chunk_index=idx,
                        heading_path=chunk_result.heading_path,
                        content=chunk_result.content,
                        token_count=chunk_result.token_count,
                        embedding=embedding,
                        language=language,
                    )
                )

        documents_processed += 1

    if not dry_run:
        await db.commit()
        if documents_processed:
            await _vacuum_chunks(db)

    elapsed_ms = int((time.perf_counter() - start) * 1000)
    return IngestOutcome(
        documents_processed=documents_processed,
        chunks_created=chunks_created,
        chunks_updated=chunks_updated,
        chunks_skipped=chunks_skipped,
        elapsed_ms=elapsed_ms,
        commit_sha=sha,
    )

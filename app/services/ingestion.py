"""Fetch the FastAPI docs from GitHub, chunk them, embed them, and upsert into Postgres.

Idempotent by content hash: unchanged files are skipped, changed files have
their chunks fully replaced, so re-running ingestion after a doc update only
recomputes what actually changed.
"""

from __future__ import annotations

import asyncio
import hashlib
import time
from dataclasses import dataclass

import httpx
from sqlalchemy import delete, select
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

GITHUB_API = "https://api.github.com"
RAW_BASE = "https://raw.githubusercontent.com"
REPO = "tiangolo/fastapi"
DOCS_PREFIX = "docs/en/docs/"
MAX_CONCURRENT_FETCHES = 8


async def resolve_commit_sha(client: httpx.AsyncClient, commit_sha: str | None = None) -> str:
    if commit_sha:
        return commit_sha
    resp = await client.get(f"{GITHUB_API}/repos/{REPO}/commits/master")
    resp.raise_for_status()
    return resp.json()["sha"]


async def list_doc_paths(client: httpx.AsyncClient, sha: str) -> list[str]:
    resp = await client.get(f"{GITHUB_API}/repos/{REPO}/git/trees/{sha}", params={"recursive": "1"})
    resp.raise_for_status()
    tree = resp.json()["tree"]
    return [
        item["path"]
        for item in tree
        if item["type"] == "blob"
        and item["path"].startswith(DOCS_PREFIX)
        and item["path"].endswith(".md")
    ]


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
    embedder: EmbeddingService,
    commit_sha: str | None = None,
    limit: int | None = None,
    dry_run: bool = False,
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
        paths = await list_doc_paths(client, sha)
        if limit:
            paths = paths[:limit]

        semaphore = asyncio.Semaphore(MAX_CONCURRENT_FETCHES)

        async def fetch(path: str) -> tuple[str, str]:
            async with semaphore:
                return path, await fetch_raw_file(client, sha, path)

        results = await asyncio.gather(*(fetch(p) for p in paths))

    for path, raw_text in results:
        # The chunker version is part of the key: otherwise a chunking change would leave
        # every unchanged doc "skipped" and silently keep its stale chunks.
        content_hash = hashlib.sha256(f"chunker-v{CHUNKER_VERSION}\n{raw_text}".encode()).hexdigest()

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
                    )
                )

        documents_processed += 1

    if not dry_run:
        await db.commit()

    elapsed_ms = int((time.perf_counter() - start) * 1000)
    return IngestOutcome(
        documents_processed=documents_processed,
        chunks_created=chunks_created,
        chunks_updated=chunks_updated,
        chunks_skipped=chunks_skipped,
        elapsed_ms=elapsed_ms,
        commit_sha=sha,
    )

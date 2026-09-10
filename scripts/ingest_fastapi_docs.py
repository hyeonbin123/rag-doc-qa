"""Repeatable, idempotent ingestion CLI for the FastAPI docs corpus.

Usage:
    python -m scripts.ingest_fastapi_docs [--commit SHA] [--limit N] [--dry-run]
"""

from __future__ import annotations

import argparse
import asyncio

from app.db.session import async_session_maker
from app.services.embedding import get_embedding_service
from app.services.ingestion import run_ingestion


async def main(commit_sha: str | None, limit: int | None, dry_run: bool) -> None:
    embedder = get_embedding_service()
    async with async_session_maker() as db:
        outcome = await run_ingestion(
            db, embedder, commit_sha=commit_sha, limit=limit, dry_run=dry_run
        )

    print(f"commit sha:          {outcome.commit_sha}")
    print(f"documents processed: {outcome.documents_processed}")
    print(f"chunks created:      {outcome.chunks_created}")
    print(f"chunks updated:      {outcome.chunks_updated}")
    print(f"documents skipped:   {outcome.chunks_skipped} (unchanged content hash)")
    print(f"elapsed:             {outcome.elapsed_ms} ms")
    if dry_run:
        print("(dry run — no database writes were made)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--commit", dest="commit_sha", default=None)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    asyncio.run(main(args.commit_sha, args.limit, args.dry_run))

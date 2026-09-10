"""Debug utility: list the FastAPI doc paths that would be ingested, without embedding anything.

Usage:
    python -m scripts.fetch_docs [--commit SHA]
"""

from __future__ import annotations

import argparse
import asyncio

import httpx

from app.services.ingestion import list_doc_paths, resolve_commit_sha


async def main(commit_sha: str | None) -> None:
    async with httpx.AsyncClient(
        timeout=30.0, headers={"User-Agent": "rag-doc-qa-ingest"}, follow_redirects=True
    ) as client:
        sha = await resolve_commit_sha(client, commit_sha)
        paths = await list_doc_paths(client, sha)

    print(f"commit: {sha}")
    print(f"doc files found: {len(paths)}")
    for path in paths:
        print(f"  {path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--commit", dest="commit_sha", default=None)
    args = parser.parse_args()
    asyncio.run(main(args.commit_sha))

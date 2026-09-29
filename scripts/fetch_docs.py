"""Debug utility: list the FastAPI doc paths that would be ingested, without embedding anything.

Usage:
    python -m scripts.fetch_docs [--commit SHA] [--languages en,ko]
"""

from __future__ import annotations

import argparse
import asyncio

import httpx

from app.services.ingestion import DOC_LANGUAGES, list_doc_paths, resolve_commit_sha


async def main(commit_sha: str | None, languages: tuple[str, ...] = DOC_LANGUAGES) -> None:
    async with httpx.AsyncClient(
        timeout=30.0, headers={"User-Agent": "rag-doc-qa-ingest"}, follow_redirects=True
    ) as client:
        sha = await resolve_commit_sha(client, commit_sha)
        paths = await list_doc_paths(client, sha, languages)

    print(f"commit: {sha}")
    print(f"doc files found: {len(paths)}")
    for path, language in paths:
        print(f"  [{language}] {path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--commit", dest="commit_sha", default=None)
    parser.add_argument(
        "--languages",
        default=",".join(DOC_LANGUAGES),
        help="comma-separated docs translations to list (default: en,ko)",
    )
    args = parser.parse_args()
    languages = tuple(lang.strip() for lang in args.languages.split(",") if lang.strip())
    asyncio.run(main(args.commit_sha, languages))

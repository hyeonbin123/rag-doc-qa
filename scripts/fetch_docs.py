"""Debug utility: list the FastAPI doc paths that would be ingested, without embedding anything.

Usage:
    python -m scripts.fetch_docs [--commit SHA] [--languages en,ko]
"""

# [파일 역할] 적재 대상 문서 목록만 확인하는 디버그용 명령. GitHub에서 FastAPI 문서 트리를 읽어 언어별로 어떤
# Markdown 파일이 적재될지 출력하고, 임베딩·DB 쓰기는 하지 않는다.
# [왜 필요한가] 전체 적재는 임베딩 때문에 몇 분이 걸리므로, 커밋이나 언어 필터를 바꿨을 때 대상 페이지가
# 맞는지 먼저 빠르게 볼 수 있게 한다.
# [설계] 목록을 고르는 로직(제외 페이지, 언어별 경로, 잘린 트리 거부)은 app/services/ingestion.py의 함수를
# 그대로 써서 실제 적재와 같은 목록이 나오게 한다. 한국어 지원 뒤 list_doc_paths가 언어 인자를 받게 바뀌었는데
# 이 스크립트만 옛 호출로 남아 TypeError로 끝나던 것을 2026-09-29에 고쳤다(커밋 0b0b578,
# tests/test_fetch_docs.py가 고정).

from __future__ import annotations

import argparse
import asyncio

# httpx: GitHub API를 비동기로 부른다. 적재 코드와 같은 클라이언트 종류라 함수를 그대로 넘길 수 있다.
import httpx

from app.services.ingestion import DOC_LANGUAGES, list_doc_paths, resolve_commit_sha


# 커밋 SHA를 정하고(--commit이 없으면 tiangolo/fastapi master 브랜치의 최신 커밋) 그 커밋의 문서 경로를
# 언어별로 출력한다.
# HTTP 설정(30초 제한, User-Agent, 리디렉션 따라가기)은 run_ingestion과 같게 둔다. GitHub API는 User-Agent가
# 없는 요청을 거부한다.
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
    # 'en,ko' 같은 쉼표 목록을 튜플로 바꾸고 빈 항목은 버린다(적재 CLI의 --languages와 같은 형식).
    languages = tuple(lang.strip() for lang in args.languages.split(",") if lang.strip())
    asyncio.run(main(args.commit_sha, languages))

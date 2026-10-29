"""디버그 도구: 아무것도 임베딩하지 않고, 적재될 FastAPI 문서 경로 목록만 보여 준다.

사용법:
    python -m scripts.fetch_docs [--commit REF] [--languages en,ko]
"""

# [파일 역할] 적재 대상 문서 목록만 확인하는 디버그용 명령. GitHub에서 FastAPI 문서 트리를 읽어 언어별로 어떤
# Markdown 파일이 적재될지 출력하고, 임베딩·DB 쓰기는 하지 않는다.
# [왜 필요한가] 전체 적재는 임베딩 때문에 몇 분이 걸리므로, 커밋이나 언어 필터를 바꿨을 때 대상 페이지가
# 맞는지 먼저 빠르게 볼 수 있게 한다.
# [설계] 목록을 고르는 로직(제외 페이지, 언어별 경로, 잘린 트리 거부)과 커밋 정하기(ref → 40자 SHA, 기본값은
# 측정에 쓴 문서 스냅숏), HTTP 클라이언트 설정은 app/services/ingestion.py의 함수를 그대로 써서 실제 적재와
# 같은 목록이 나오게 한다. 한국어 지원 뒤 list_doc_paths가 언어 인자를 받게 바뀌었는데 이 스크립트만 옛 호출로
# 남아 TypeError로 끝나던 것을 2026-09-29에 고쳤다(커밋 0b0b578, tests/test_fetch_docs.py가 고정).

from __future__ import annotations

import argparse
import asyncio

# 적재와 같은 GitHub 클라이언트·커밋 해석·경로 목록 함수와 ref 형식 검사.
from app.schemas.text import validate_git_ref
from app.services.ingestion import (
    DOC_LANGUAGES,
    DOCS_SNAPSHOT_COMMIT,
    github_client,
    list_doc_paths,
    resolve_commit_sha,
)


# 커밋 SHA를 정하고(--commit이 없으면 적재와 같은 기본값: 설정 FASTAPI_DOCS_COMMIT_SHA, 비어 있으면 측정
# 스냅숏 DOCS_SNAPSHOT_COMMIT) 그 커밋의 문서 경로를 언어별로 출력한다. 출력의 commit 줄은 ref를 해석한 40자
# SHA다.
async def main(commit_sha: str | None, languages: tuple[str, ...] = DOC_LANGUAGES) -> None:
    async with github_client() as client:
        sha = await resolve_commit_sha(client, commit_sha)
        paths = await list_doc_paths(client, sha, languages)

    print(f"commit: {sha}")
    print(f"doc files found: {len(paths)}")
    for path, language in paths:
        print(f"  [{language}] {path}")


# argparse type 함수: --commit 값의 형식을 적재 명령(scripts/ingest_fastapi_docs.py)과 같은 규칙으로 검사한다.
def git_ref_argument(value: str) -> str:
    try:
        return validate_git_ref(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc


# 명령줄 옵션 정의. 테스트가 sys.argv 없이 파서를 만들 수 있게 함수로 둔다(tests/test_fetch_docs.py).
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "적재될 FastAPI 문서(tiangolo/fastapi의 docs/<언어>/docs/) 경로 목록만 GitHub 트리에서 "
            "읽어 보여 준다. 임베딩·DB 쓰기는 하지 않는다."
        )
    )
    parser.add_argument(
        "--commit",
        dest="commit_sha",
        type=git_ref_argument,
        default=None,
        metavar="REF",
        help=(
            "목록을 볼 tiangolo/fastapi의 브랜치·태그·커밋 SHA(짧은 SHA도 됨). GitHub에 물어 "
            "40자 SHA로 바꾼다. 주지 않으면 적재와 같은 기본값(설정 FASTAPI_DOCS_COMMIT_SHA, "
            f"비어 있으면 측정 스냅숏 {DOCS_SNAPSHOT_COMMIT[:7]}). 최신 문서는 --commit master."
        ),
    )
    parser.add_argument(
        "--languages",
        default=",".join(DOC_LANGUAGES),
        help="목록을 볼 문서 번역 언어, 쉼표로 구분(기본값: en,ko)",
    )
    return parser


if __name__ == "__main__":
    args = build_parser().parse_args()
    # 'en,ko' 같은 쉼표 목록을 튜플로 바꾸고 빈 항목은 버린다(적재 CLI의 --languages와 같은 형식).
    languages = tuple(lang.strip() for lang in args.languages.split(",") if lang.strip())
    asyncio.run(main(args.commit_sha, languages))

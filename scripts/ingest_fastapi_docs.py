"""FastAPI 문서 코퍼스를 적재하는 명령행 도구. 몇 번을 다시 돌려도 결과가 같다(멱등).

사용법:
    python -m scripts.ingest_fastapi_docs [--commit SHA] [--limit N] [--dry-run]
                                          [--languages en,ko]
"""

# [파일 역할] FastAPI 공식 문서를 GitHub에서 받아 청킹·임베딩한 뒤 DB에 적재하는 명령행 진입점(README '3. 문서
# 수집'). 실제 일은 app/services/ingestion.py의 run_ingestion이 하고, 이 파일은 옵션을 받아 넘기고 결과를
# 출력만 한다.
# [왜 따로 두나] 같은 적재 로직을 관리자 API(app/routers/documents.py)와 이 CLI가 함께 쓴다. 청킹도 앱과 같은
# app/services/chunking.py를 쓰므로 CLI로 적재한 청크와 앱이 다루는 청크가 같은 규칙으로 만들어진다.
# [동작 요약] 내용 해시(청커 버전 + 임베딩 모델 identity + 원문)가 같은 문서는 건너뛰어 다시 실행해도 바뀐
# 문서만 처리한다. --limit 없이 전체를 적재하면 적재한 언어에서 트리에 없는 문서를 지우고, 바뀐 문서가 있으면
# VACUUM (ANALYZE)를 돌린다.
# [실행] 컨테이너 안에서는 uv run 대신 python -m으로 실행한다. uv run은 실행할 때마다 dev 의존성까지 설치하려
# 하기 때문이다(README).

from __future__ import annotations

import argparse
import asyncio

# 앱의 DB 세션, 언어별 임베딩 서비스 조회 함수, 적재 함수를 그대로 쓴다. 지원 언어 목록(DOC_LANGUAGES)이
# --languages의 기본값이다.
from app.db.session import async_session_maker
from app.services.embedding import get_embedding_service
from app.services.ingestion import DOC_LANGUAGES, run_ingestion


# 적재를 한 번 실행하고 결과를 사람이 읽기 좋게 출력한다.
# get_embedding_service를 함수째 넘기는 이유: run_ingestion이 문서마다 언어에 맞는 모델(영어 bge-small, 한국어
# granite-311m)을 골라 쓰기 때문이다.
# dry_run이면 DB에 쓰지 않고 처리·삭제될 개수만 센다.
async def main(
    commit_sha: str | None, limit: int | None, dry_run: bool, languages: tuple[str, ...]
) -> None:
    async with async_session_maker() as db:
        outcome = await run_ingestion(
            db,
            get_embedding_service,
            commit_sha=commit_sha,
            limit=limit,
            dry_run=dry_run,
            languages=languages,
        )

    # 어떤 모델로 적재했는지 먼저 출력한다. 한국어 모델을 바꾸면 해시가 달라져 그 언어 문서가 모두 다시
    # 임베딩되므로 확인용으로 남긴다.
    # 'documents skipped' 줄에 찍히는 outcome.chunks_skipped는 이름과 달리 해시가 같아 건너뛴 문서
    # 수다(run_ingestion이 문서마다 1씩 센다).
    models = ", ".join(f"{lang}={get_embedding_service(lang).model_name}" for lang in languages)
    print(f"embedding models:    {models}")
    print(f"commit sha:          {outcome.commit_sha}")
    print(f"documents processed: {outcome.documents_processed}")
    print(f"documents deleted:   {outcome.documents_deleted} (no longer listed upstream)")
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
    parser.add_argument(
        "--languages",
        default=",".join(DOC_LANGUAGES),
        help="적재할 문서 번역 언어, 쉼표로 구분(기본값: en,ko)",
    )
    args = parser.parse_args()
    # 'en,ko' 같은 쉼표 목록을 튜플로 바꾼다. --languages ko처럼 한 언어만 다시 적재할 수 있다(v13 단계 B에서
    # 한국어 임베딩을 바꾼 뒤 한국어만 재적재).
    languages = tuple(lang.strip() for lang in args.languages.split(",") if lang.strip())
    asyncio.run(main(args.commit_sha, args.limit, args.dry_run, languages))

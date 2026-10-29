"""FastAPI 문서 코퍼스를 적재하는 명령행 도구. 몇 번을 다시 돌려도 결과가 같다(멱등).

사용법:
    python -m scripts.ingest_fastapi_docs [--commit REF] [--limit N] [--dry-run]
                                          [--languages en,ko]

종료 코드: 0 성공, 1 같은 DB에서 다른 적재가 진행 중(잠금, 아무것도 바꾸지 않음) 또는 적재 중
오류(트레이스백), 2 옵션 오류.
"""

# [파일 역할] FastAPI 공식 문서를 GitHub에서 받아 청킹·임베딩한 뒤 DB에 적재하는 명령행 진입점(README '3. 문서
# 수집'). 실제 일은 app/services/ingestion.py의 run_ingestion이 하고, 이 파일은 옵션을 검사해 넘기고 결과를
# 출력만 한다.
# [왜 따로 두나] 같은 적재 로직을 관리자 API(app/routers/documents.py)와 이 CLI가 함께 쓴다. 청킹도 앱과 같은
# app/services/chunking.py를 쓰므로 CLI로 적재한 청크와 앱이 다루는 청크가 같은 규칙으로 만들어진다. 옵션
# 검사도 관리자 API의 요청 본문(IngestRequest)과 같은 규칙이다: --commit은 validate_git_ref, --limit은 1 이상.
# [동작 요약] 내용 해시(청커 버전 + 임베딩 모델 identity + 원문)가 같은 문서는 건너뛰어 다시 실행해도 바뀐
# 문서만 처리한다. --limit 없이 전체를 적재하면 적재한 언어에서 트리에 없는 문서를 지우고, 바뀐 문서가 있으면
# VACUUM (ANALYZE)를 돌린다. --commit이 없으면 설정 FASTAPI_DOCS_COMMIT_SHA, 그것도 비어 있으면 측정에 쓴 문서
# 스냅숏(DOCS_SNAPSHOT_COMMIT)을 적재한다. 최신 문서는 --commit master로 받는다.
# [실행] 컨테이너 안에서는 uv run 대신 python -m으로 실행한다. uv run은 실행할 때마다 dev 의존성까지 설치하려
# 하기 때문이다(README).

from __future__ import annotations

import argparse
import asyncio
import sys

# 앱의 DB 세션, ref 형식 검사, 언어별 임베딩 서비스 조회 함수, 적재 함수와 상수를 그대로 쓴다. 지원 언어
# 목록(DOC_LANGUAGES)이 --languages의 기본값이다.
from app.db.session import async_session_maker
from app.schemas.text import validate_git_ref
from app.services.embedding import get_embedding_service
from app.services.ingestion import (
    DOC_LANGUAGES,
    DOCS_SNAPSHOT_COMMIT,
    IngestionAlreadyRunning,
    run_ingestion,
)


# argparse type 함수: --commit 값이 브랜치·태그·커밋 SHA로 안전한 형식인지 관리자 API와 같은 규칙으로
# 검사한다. 어긋나면 ArgumentTypeError를 내 argparse가 이유와 사용법을 찍고 종료 코드 2로 끝낸다.
def git_ref_argument(value: str) -> str:
    try:
        return validate_git_ref(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc


# argparse type 함수: --limit 값은 1 이상의 정수여야 한다. 적재 함수도 1 미만을 ValueError로 거부하지만,
# 여기서 막으면 사용법 오류(종료 코드 2)로 바로 끝나 GitHub·DB에 닿지 않는다.
def positive_int_argument(value: str) -> int:
    try:
        number = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"invalid int value: {value!r}") from exc
    if number < 1:
        raise argparse.ArgumentTypeError("must be at least 1 (omit --limit to ingest every page)")
    return number


# 'en,ko' 같은 쉼표 목록을 튜플로 바꾸고 빈 항목은 버린다. --languages ko처럼 한 언어만 다시 적재할 수
# 있다(v13 단계 B에서 한국어 임베딩을 바꾼 뒤 한국어만 재적재). scripts/fetch_docs.py의 --languages와 같은
# 형식이다.
def parse_languages(value: str) -> tuple[str, ...]:
    return tuple(lang.strip() for lang in value.split(",") if lang.strip())


# 명령줄 옵션 정의. 테스트가 sys.argv 없이 파서를 만들 수 있게 함수로 둔다(tests/test_ingest_cli.py).
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "FastAPI 공식 문서(tiangolo/fastapi의 docs/<언어>/docs/)를 GitHub에서 받아 청킹·임베딩한 뒤 DB에 "
            "적재한다. 내용 해시가 같은 문서는 건너뛰므로 다시 실행해도 바뀐 문서만 처리한다."
        ),
        epilog=(
            "종료 코드: 0 성공, 1 같은 DB에서 다른 적재(관리자 API 또는 다른 CLI 실행)가 진행 "
            "중(이때는 아무것도 바꾸지 않고 바로 끝남)이거나 적재 중 오류(트레이스백), 2 옵션 오류. "
            "--limit 없이 전체를 적재하면 적재한 언어에서 GitHub 트리에 더는 없는 문서를 청크와 함께 지우고, "
            "바뀐 문서가 있으면 VACUUM (ANALYZE)를 돌린다."
        ),
    )
    parser.add_argument(
        "--commit",
        dest="commit_sha",
        type=git_ref_argument,
        default=None,
        metavar="REF",
        help=(
            "적재할 tiangolo/fastapi의 브랜치·태그·커밋 SHA(짧은 SHA도 됨). GitHub에 물어 40자 커밋 "
            "SHA로 바꾼 뒤 모든 문서를 그 커밋에서 받고 문서 행의 source_commit_sha에 저장한다. 주지 "
            "않으면 설정 FASTAPI_DOCS_COMMIT_SHA, 그것도 비어 있으면 측정에 쓴 문서 스냅숏 "
            f"{DOCS_SNAPSHOT_COMMIT[:7]}. 최신 문서는 --commit master."
        ),
    )
    parser.add_argument(
        "--limit",
        type=positive_int_argument,
        default=None,
        metavar="N",
        help=(
            "트리 목록의 앞에서 N개 문서만 처리한다(시험용, 1 이상). 이때는 트리에 없는 문서를 지우는 단계를 "
            "건너뛴다."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="DB를 바꾸지 않고 처리·삭제될 문서 수와 청크 수만 센다(적재 잠금도 잡지 않는다).",
    )
    parser.add_argument(
        "--languages",
        default=",".join(DOC_LANGUAGES),
        help="적재할 문서 번역 언어, 쉼표로 구분(기본값: en,ko). 삭제 단계도 이 언어 범위 안에서만 한다.",
    )
    return parser


# 적재를 한 번 실행하고 결과를 사람이 읽기 좋게 출력한 뒤 종료 코드를 돌려준다. get_embedding_service를 함수째
# 넘기는 이유: run_ingestion이 문서마다 언어에 맞는 모델(영어 bge-small, 한국어 granite-311m)을 골라 쓰기
# 때문이다. dry_run이면 DB에 쓰지 않고 처리·삭제될 개수만 센다. 같은 DB에서 다른 적재가 진행
# 중이면(IngestionAlreadyRunning) 메시지를 stderr에 적고 1을 돌려준다(아무것도 바꾸지 않았다).
async def main(
    commit_sha: str | None, limit: int | None, dry_run: bool, languages: tuple[str, ...]
) -> int:
    async with async_session_maker() as db:
        try:
            outcome = await run_ingestion(
                db,
                get_embedding_service,
                commit_sha=commit_sha,
                limit=limit,
                dry_run=dry_run,
                languages=languages,
            )
        except IngestionAlreadyRunning as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1

    # 어떤 모델로 적재했는지 먼저 출력한다. 한국어 모델을 바꾸면 해시가 달라져 그 언어 문서가 모두 다시
    # 임베딩되므로 확인용으로 남긴다. commit sha 줄은 ref를 해석한 40자 SHA다.
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
    return 0


if __name__ == "__main__":
    args = build_parser().parse_args()
    raise SystemExit(
        asyncio.run(main(args.commit_sha, args.limit, args.dry_run, parse_languages(args.languages)))
    )

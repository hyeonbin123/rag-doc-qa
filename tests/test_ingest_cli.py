"""scripts/ingest_fastapi_docs.py: 적재 명령의 옵션 검증과 종료 코드 테스트."""

# [테스트 묶음] 적재 명령(scripts/ingest_fastapi_docs.py)의 옵션 파서와 종료 코드를 본다. 실제 적재(GitHub,
# 임베딩, DB)는 돌리지 않는다: 옵션 파서는 그대로 쓰고, 종료 코드 확인은 run_ingestion을 가짜로 바꿔 끼운다.
# [왜 중요한가] 예전에는 --limit이 type=int만이라 0·음수가 적재 함수까지 들어가 '전체 적재 + 삭제'나 '뒤 n개를
# 빼고 처리'가 됐고, --commit은 아무 문자열이든 받아 GitHub URL 경로에 그대로 넣었다(2026-10-29, 관리자 API의
# IngestRequest와 같은 규칙으로 맞춤). 다른 적재가 진행 중일 때(어드바이저리 잠금)는 종료 코드 1로 끝난다.

import pytest

# 적재 모듈('적재가 이미 진행 중' 예외)과 테스트 대상 명령 모듈.
from app.services import ingestion
from scripts import ingest_fastapi_docs as cli


# 명령줄 옵션을 파싱한다(sys.argv 대신 목록을 넘긴다).
def parse(argv: list[str]):
    return cli.build_parser().parse_args(argv)


# 1 미만이거나 정수가 아닌 --limit, 안전하지 않은 형식의 --commit('..'·'.' 세그먼트, 공백, 101자, 빈 값)은
# argparse 사용법 오류(종료 코드 2)로 끝나야 한다. 적재 함수에 닿기 전에 막는다.
@pytest.mark.parametrize(
    "argv",
    [
        ["--limit", "0"],
        ["--limit", "-1"],
        ["--limit", "abc"],
        ["--commit", "a..b"],
        ["--commit", "../x"],
        ["--commit", "."],
        ["--commit", "./x"],
        ["--commit", "x y"],
        ["--commit", "a" * 101],
        ["--commit", ""],
    ],
)
def test_bad_options_are_usage_errors(argv, capsys):
    with pytest.raises(SystemExit) as exc:
        parse(argv)

    assert exc.value.code == 2
    assert "usage:" in capsys.readouterr().err


# 브랜치 이름·양수 limit·dry run·한 언어는 그대로 파싱된다(--commit master 같은 기존 사용법을 막지 않는다).
def test_valid_options_are_parsed():
    args = parse(["--commit", "master", "--limit", "3", "--dry-run", "--languages", "ko"])

    assert (args.commit_sha, args.limit, args.dry_run) == ("master", 3, True)
    assert cli.parse_languages(args.languages) == ("ko",)


# 옵션을 하나도 주지 않으면 commit·limit은 None(적재 함수가 기본 ref와 전체 적재로 처리), dry run은 꺼짐,
# 언어는 지원 언어 전체다.
def test_defaults_leave_the_choices_to_the_ingestion():
    args = parse([])

    assert (args.commit_sha, args.limit, args.dry_run) == (None, None, False)
    assert cli.parse_languages(args.languages) == ingestion.DOC_LANGUAGES


# 같은 DB에서 다른 적재가 진행 중이면(IngestionAlreadyRunning) 오류 메시지를 stderr에 적고 종료 코드 1을
# 돌려준다. run_ingestion은 세션에 아무 SQL도 보내지 않는 가짜라 DB 연결 없이 돈다.
@pytest.mark.asyncio
async def test_a_running_ingestion_ends_with_exit_code_1(monkeypatch, capsys):
    async def already_running(*args, **kwargs):
        raise ingestion.IngestionAlreadyRunning("another ingestion is already running")

    monkeypatch.setattr(cli, "run_ingestion", already_running)

    code = await cli.main(None, None, False, ("en",))

    assert code == 1
    assert "already running" in capsys.readouterr().err

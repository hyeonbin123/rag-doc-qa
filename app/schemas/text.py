# [파일 역할] 요청 문자열에 공통으로 붙이는 검증 타입: DB에 저장될 문자열의 NUL 거부(NulFreeStr)와 적재 대상
# ref(브랜치·태그·커밋 SHA)의 형식 검사(validate_git_ref, GitRefStr)를 정의한다.
# [왜 필요한가] OWASP ZAP 1차 스캔에서 질문에 NUL 문자가 있으면 /query/ask가 500을 내는 것이
# 발견됐다(docs/security-scan.md). PostgreSQL text 타입은 U+0000을 저장할 수 없어서, 생성까지 다 끝난 뒤 질문
# 기록을 커밋할 때 asyncpg 오류가 났다. 입력 단계에서 422로 막으면 LLM 호출 낭비도 없다. ref 검사는
# 2026-10-29에 더했다: 적재 요청의 commit_sha가 GitHub URL 경로에 그대로 들어가는데 형식 검사가 없어 '..'
# 세그먼트가 다른 API 경로를 가리키거나 공백·'?'가 경로를 끊을 수 있었고, 길이 제한도 없었다.
# [연결] AskRequest.question(app/schemas/query.py), IngestRequest.commit_sha(app/schemas/document.py)가 쓴다.
# validate_git_ref는 적재 명령(scripts/ingest_fastapi_docs.py, scripts/fetch_docs.py)의 --commit과
# app/services/ingestion.py의 resolve_commit_sha도 같은 규칙으로 쓴다. 로그인 이메일은
# app/services/users.py에서 따로 막는다.

import re
from typing import Annotated

from pydantic import AfterValidator


# NUL이 있으면 ValueError를 낸다. pydantic이 이 오류를 검증 오류로 바꿔 FastAPI가 422로 응답한다.
def reject_nul(value: str) -> str:
    # PostgreSQL text는 U+0000을 담을 수 없다. 이런 값은 그 행을 쓸 때에야 실패하는데, 그때는 요청한
    # 작업(질문이면 LLM 답변 생성 전체)을 이미 다 한 뒤라 500이 된다. 그래서 입력 단계에서 막는다.
    if "\x00" in value:
        raise ValueError("must not contain the NUL character (U+0000)")
    return value


# str에 검증기를 붙인 재사용 타입. AfterValidator라 pydantic의 기본 str 타입 검증을 통과한 값에 실행된다. 끝의
# 문자열은 이 타입의 설명(docstring 역할)이다. 실행 중에는 쓰이지 않고 OpenAPI 스키마에도 나가지 않는다.
NulFreeStr = Annotated[str, AfterValidator(reject_nul)]
"""앱이 PostgreSQL에 저장하는 요청 문자열(NUL 문자 U+0000이 있으면 거부한다)."""


# Git ref(브랜치·태그·짧거나 긴 커밋 SHA)로 받는 문자열의 형식. 영숫자·'.'·'_'·'-'로 된 조각을 '/'로 이은 꼴만
# 허용하고, 조각은 '.'으로 시작할 수 없다(앞뒤 '/'와 'a//b' 같은 빈 조각, '.'·'.hidden' 같은 조각은 불일치).
# 조각 첫 글자 규칙은 git check-ref-format의 '조각은 점으로 시작할 수 없다'와 같고, URL 경로의 점
# 세그먼트('.')도 함께 막는다. 길이 상한 100은 git이 허용하는 길이보다 훨씬 짧지만 실제 브랜치·태그 이름에는
# 충분하고, 적재는 어차피 이 값을 GitHub에 물어 40자 SHA로 바꾼 뒤에만 저장한다.
GIT_REF_MAX_LENGTH = 100
_GIT_REF_PART = r"[A-Za-z0-9_-][A-Za-z0-9._-]*"
_GIT_REF_RE = re.compile(rf"{_GIT_REF_PART}(?:/{_GIT_REF_PART})*")


# ref 형식이 안전하지 않으면 ValueError, 맞으면 그대로 돌려준다. 보안 통제가 아니라 정확성 검사다: 신뢰 경계는
# 관리자 토큰이고, 40자 16진수만 받아도 GitHub는 포크 네트워크의 커밋을 원 저장소 경로로 내주므로 다른 내용의
# 주입은 막지 못한다. 막는 것은 (1) '..'·'.' 세그먼트: 값이 URL 경로에 들어가면 httpx가 점 세그먼트를 정규화해
# api.github.com의 다른 경로를 요청하게 된다('../x'는 commits/ 밖으로 나가고, '.' 하나는 커밋 하나가 아니라
# 커밋 목록 경로 .../commits가 된다) (2) 공백·'?'·'#' 등: 경로를 끊거나 쿼리로 바뀐다 (3) 빈 값과 지나치게 긴
# 값: 실제 ref가 아니다. git 자체도 '..', 점으로 시작하는 조각, 제어 문자, 공백, '~', '^', ':', '?', '*', '[',
# '\'을 ref 이름에 허용하지 않는다(git check-ref-format).
def validate_git_ref(value: str) -> str:
    if not value or len(value) > GIT_REF_MAX_LENGTH:
        raise ValueError(f"must be a git ref of 1 to {GIT_REF_MAX_LENGTH} characters")
    if ".." in value or _GIT_REF_RE.fullmatch(value) is None:
        raise ValueError(
            "must be a branch, tag or commit sha: letters, digits, '.', '_', '-' and inner '/' only, "
            "without '..' or a part that starts with '.'"
        )
    return value


# IngestRequest.commit_sha의 타입. NUL 검사(NulFreeStr) 다음에 ref 형식 검사를 붙인다. 끝의 문자열은 이 타입의
# 설명(docstring 역할)이다(NulFreeStr와 같이 실행 중에는 쓰이지 않음).
GitRefStr = Annotated[NulFreeStr, AfterValidator(validate_git_ref)]
"""적재가 받는 tiangolo/fastapi의 브랜치·태그·커밋 SHA(validate_git_ref의 형식만 받는다)."""

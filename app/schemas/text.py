# [파일 역할] DB에 저장될 요청 문자열에 공통으로 붙이는 검증 타입(NulFreeStr)을 정의한다.
# [왜 필요한가] OWASP ZAP 1차 스캔에서 질문에 NUL 문자가 있으면 /query/ask가 500을 내는 것이
# 발견됐다(docs/security-scan.md). PostgreSQL text 타입은 U+0000을 저장할 수 없어서, 생성까지 다 끝난 뒤 질문
# 기록을 커밋할 때 asyncpg 오류가 났다. 입력 단계에서 422로 막으면 LLM 호출 낭비도 없다.
# [연결] AskRequest.question(app/schemas/query.py), IngestRequest.commit_sha(app/schemas/document.py)가 쓴다.
# 로그인 이메일은 app/services/users.py에서 따로 막는다.

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
# 문자열은 이 타입의 설명(docstring 역할)이고, 뜻은 "앱이 PostgreSQL에 저장하는 요청 문자열"이다.
NulFreeStr = Annotated[str, AfterValidator(reject_nul)]
"""Request text the app stores in PostgreSQL."""

# [파일 역할] 사용자가 입력한 이메일로 계정을 찾는 공용 조회 함수.
# [왜 따로 두나] 로그인(app/routers/auth.py)과 데모 계정 시드 스크립트(scripts/seed_demo_user.py)가 같은
# 규칙으로 계정을 찾아야 한다. 가입은 정규화한 주소를 저장하지만 예전 시드 스크립트가 만든 행에는 입력한
# 그대로의 주소가 있어서, 정규화한 형태만 찾으면 그런 계정이 로그인하지 못하는 문제가 있었다(아래 docstring).

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.auth import normalize_email


async def find_user_by_email(db: AsyncSession, typed: str) -> User | None:
    """입력한 주소가 어느 계정의 것인지 찾는다.

    가입은 EmailStr로 정규화한 주소를 저장하지만, 예전 버전의 scripts/seed_demo_user.py가 만든 행에는
    입력한 그대로의 주소가 있다("Demo@Example.COM"). 두 철자를 모두 찾되 입력한 철자를 우선하므로, 정규화가
    생기기 전에 어떤 행과 맞던 로그인은 지금도 그 행에 닿는다. 정규화한 철자는 맞는 경우를 더할 뿐이다.
    """
    # NUL 문자가 든 username은 DB에 묻지 않고 '없음'으로 처리한다. 그대로 질의 파라미터로 보내면 PostgreSQL이
    # 거부해 로그인이 500이 됐다(OWASP ZAP 지적 후속 수정). 결과적으로 로그인은 401이 된다.
    if "\x00" in typed:
        return None  # 저장된 주소에는 U+0000이 없고, PostgreSQL은 이를 파라미터로 받지 않는다
    # 후보 1순위는 입력한 그대로, 2순위는 정규화한 형태(주소 형식이 아니면 정규화 없이 그대로만 찾는다).
    candidates = [typed]
    try:
        normalized = normalize_email(typed)
    except ValueError:
        normalized = None  # 주소 형식이 아니다: 저장된 값과 정확히 같은 경우만 맞을 수 있다
    if normalized is not None and normalized != typed:
        candidates.append(normalized)

    # 두 후보를 IN 한 번으로 조회한 뒤, 후보 순서대로 처음 맞는 행을 고른다. 그래서 같은 주소가 원문 행과
    # 정규화 행으로 둘 다 있어도 입력한 철자와 정확히 같은 행이 우선한다.
    rows = await db.scalars(select(User).where(User.email.in_(candidates)))
    by_email = {user.email: user for user in rows}
    return next((by_email[email] for email in candidates if email in by_email), None)

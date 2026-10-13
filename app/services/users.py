# [파일 역할] 사용자가 입력한 이메일로 계정을 찾는 공용 조회 함수.
# [왜 따로 두나] 로그인(app/routers/auth.py)과 데모 계정 시드 스크립트(scripts/seed_demo_user.py)가 같은
# 규칙으로 계정을 찾아야 한다. 가입은 정규화한 주소를 저장하지만 예전 시드 스크립트가 만든 행에는 입력한
# 그대로의 주소가 있어서, 정규화한 형태만 찾으면 그런 계정이 로그인하지 못하는 문제가 있었다(아래 docstring).

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.auth import normalize_email


async def find_user_by_email(db: AsyncSession, typed: str) -> User | None:
    """Find the account a typed address belongs to.

    Registration stores the EmailStr-normalized address, but rows made by earlier
    versions of scripts/seed_demo_user.py hold the address exactly as typed
    ("Demo@Example.COM"). Both spellings are looked up and the typed one wins, so a
    login that matched a row before normalization existed still reaches that row;
    the normalized spelling only adds matches.
    """
    # NUL 문자가 든 username은 DB에 묻지 않고 '없음'으로 처리한다. 그대로 질의 파라미터로 보내면 PostgreSQL이
    # 거부해 로그인이 500이 됐다(OWASP ZAP 지적 후속 수정). 결과적으로 로그인은 401이 된다.
    if "\x00" in typed:
        return None  # no stored address holds U+0000, and PostgreSQL rejects it as a parameter
    # 후보 1순위는 입력한 그대로, 2순위는 정규화한 형태(주소 형식이 아니면 정규화 없이 그대로만 찾는다).
    candidates = [typed]
    try:
        normalized = normalize_email(typed)
    except ValueError:
        normalized = None  # not an address: only an exact stored match can apply
    if normalized is not None and normalized != typed:
        candidates.append(normalized)

    # 두 후보를 IN 한 번으로 조회한 뒤, 후보 순서대로 처음 맞는 행을 고른다. 그래서 같은 주소가 원문 행과
    # 정규화 행으로 둘 다 있어도 입력한 철자와 정확히 같은 행이 우선한다.
    rows = await db.scalars(select(User).where(User.email.in_(candidates)))
    by_email = {user.email: user for user in rows}
    return next((by_email[email] for email in candidates if email in by_email), None)

"""손으로 해 보는 로컬 테스트용 데모 사용자를 만든다.

사용법:
    python -m scripts.seed_demo_user demo@example.com password123
"""

# [파일 역할] 로컬에서 바로 로그인해 볼 수 있게 데모 계정 하나를 만드는 명령(README '4. 데모 사용자 생성').
# [왜 이렇게 만들었나] 예전 버전은 입력한 주소를 그대로 저장해서, 로그인이 EmailStr 정규화로 조회하도록 바뀐
# 뒤 'Demo@Example.COM' 같은 계정이 로그인하지 못하는 문제가 있었다(커밋 1d520fb).
# 그래서 지금은 가입(/auth/register)과 같은 정규화 형태로 저장하고, 이미 있는지 볼 때도 로그인과 같은 조회
# 함수를 쓴다.
# [연결] 로직은 seed_user로 분리해 tests/test_seed_demo_user.py가 DB로 직접 검증한다.

from __future__ import annotations

import argparse
import asyncio

# SQLAlchemy 비동기 세션 타입. seed_user가 테스트의 세션도 받을 수 있게 인자로 받는다.
from sqlalchemy.ext.asyncio import AsyncSession

# 앱의 세션·사용자 모델과 함께, 가입과 같은 정규화(normalize_email)와 비밀번호 규칙(UserRegister), 같은 bcrypt
# 해시(hash_password), 로그인과 같은 조회(find_user_by_email)를 가져와 앱과 다른 규칙이 생기지 않게 한다.
from app.db.session import async_session_maker
from app.models.user import User
from app.schemas.auth import MIN_PASSWORD_LENGTH, UserRegister, normalize_email
from app.services.security import MAX_PASSWORD_BYTES, hash_password
from app.services.users import find_user_by_email


# 계정을 만들거나 이미 있는 계정을 찾아 (사용자, 새로 만들었는지)를 돌려준다.
# 이미 있으면 비밀번호를 바꾸지 않고 그 행을 그대로 돌려준다. 예전 스크립트가 입력 그대로 저장한 행도 찾으므로
# 같은 사람의 계정이 두 개 생기지 않는다.
# 비밀번호는 가입 API와 같은 규칙(8자 이상, UTF-8 72바이트 이하)으로 먼저 검사한다. 예전에는 검사하지 않아
# 짧은 비밀번호 계정이 만들어졌고, 72바이트를 넘으면 bcrypt 5의 ValueError traceback으로 끝났다.
async def seed_user(db: AsyncSession, email: str, password: str) -> tuple[User, bool]:
    """(사용자, 새로 만들었는지)를 돌려준다. 주소는 /auth/register가 저장하는 형태로 저장한다.

    이미 있는 사용자인지는 로그인과 같은 조회 함수로 확인하므로, 예전 버전의 이 스크립트가 입력 그대로
    저장한 행도 찾는다.
    """
    # 먼저 정규화와 비밀번호 검사부터 해서, 가입이 거부할 값이면 DB를 건드리기 전에 ValueError(pydantic
    # ValidationError)로 끝낸다.
    stored_email = normalize_email(email)  # 주소 형식이 아니면 ValueError
    UserRegister(email=stored_email, password=password)  # /auth/register가 거부할 값이면 ValueError
    existing = await find_user_by_email(db, email)
    if existing is not None:
        return existing, False

    # 저장은 정규화한 주소로, 비밀번호는 bcrypt 해시로만 한다. 앱의 가입 API는 bcrypt를 스레드에서
    # 돌리지만(README 설계 판단), 이 스크립트는 다른 요청을 함께 처리하지 않으므로 그대로 호출한다.
    user = User(email=stored_email, hashed_password=hash_password(password))
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user, True


# 세션을 열어 seed_user를 부르고, 새로 만들었는지 이미 있었는지 출력한다.
async def main(email: str, password: str) -> None:
    async with async_session_maker() as db:
        user, created = await seed_user(db, email, password)
    if created:
        print(f"created user {user.email} (id={user.id})")
    else:
        print(f"user {user.email} already exists (id={user.id})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("email")
    parser.add_argument("password")
    args = parser.parse_args()
    # 주소 형식이나 비밀번호가 가입 규칙에 맞지 않으면 traceback 대신 argparse의 사용법 오류로 친절하게
    # 끝낸다.
    try:
        email = normalize_email(args.email)
    except ValueError:
        parser.error(f"not a valid email address: {args.email!r}")
    try:
        UserRegister(email=email, password=args.password)
    except ValueError:
        parser.error(
            f"the password must be at least {MIN_PASSWORD_LENGTH} characters and at most "
            f"{MAX_PASSWORD_BYTES} bytes in UTF-8, as /auth/register requires"
        )
    asyncio.run(main(args.email, args.password))

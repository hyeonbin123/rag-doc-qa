"""Create a demo user for manual/local testing.

Usage:
    python -m scripts.seed_demo_user demo@example.com password123
"""

from __future__ import annotations

import argparse
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session_maker
from app.models.user import User
from app.schemas.auth import normalize_email
from app.services.security import hash_password
from app.services.users import find_user_by_email


async def seed_user(db: AsyncSession, email: str, password: str) -> tuple[User, bool]:
    """Return (user, created). The address is stored the way /auth/register stores it.

    The existing-user check goes through the same lookup as login, so it also finds a
    row an earlier version of this script stored exactly as typed.
    """
    stored_email = normalize_email(email)  # ValueError if it is not an address
    existing = await find_user_by_email(db, email)
    if existing is not None:
        return existing, False

    user = User(email=stored_email, hashed_password=hash_password(password))
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user, True


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
    try:
        normalize_email(args.email)
    except ValueError:
        parser.error(f"not a valid email address: {args.email!r}")
    asyncio.run(main(args.email, args.password))

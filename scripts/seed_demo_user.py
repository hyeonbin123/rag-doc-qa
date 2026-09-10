"""Create a demo user for manual/local testing.

Usage:
    python -m scripts.seed_demo_user demo@example.com password123
"""

from __future__ import annotations

import argparse
import asyncio

from sqlalchemy import select

from app.db.session import async_session_maker
from app.models.user import User
from app.services.security import hash_password


async def main(email: str, password: str) -> None:
    async with async_session_maker() as db:
        existing = await db.scalar(select(User).where(User.email == email))
        if existing is not None:
            print(f"user {email} already exists (id={existing.id})")
            return

        user = User(email=email, hashed_password=hash_password(password))
        db.add(user)
        await db.commit()
        await db.refresh(user)
        print(f"created user {email} (id={user.id})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("email")
    parser.add_argument("password")
    args = parser.parse_args()
    asyncio.run(main(args.email, args.password))

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
    candidates = [typed]
    try:
        normalized = normalize_email(typed)
    except ValueError:
        normalized = None  # not an address: only an exact stored match can apply
    if normalized is not None and normalized != typed:
        candidates.append(normalized)

    rows = await db.scalars(select(User).where(User.email.in_(candidates)))
    by_email = {user.email: user for user in rows}
    return next((by_email[email] for email in candidates if email in by_email), None)

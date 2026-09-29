import pytest
from sqlalchemy import func, select

from app.models.user import User
from app.services.security import hash_password
from scripts.seed_demo_user import seed_user


@pytest.mark.asyncio
async def test_seed_stores_the_email_the_way_registration_does(client, db_session):
    user, created = await seed_user(db_session, "Heidi@Example.COM", "supersecret1")
    assert created
    assert user.email == "Heidi@example.com"

    # The same string then conflicts at registration and logs in, as for a registered user.
    register_resp = await client.post(
        "/auth/register", json={"email": "Heidi@Example.COM", "password": "supersecret1"}
    )
    assert register_resp.status_code == 409
    for username in ("Heidi@Example.COM", "Heidi@example.com"):
        resp = await client.post(
            "/auth/login", data={"username": username, "password": "supersecret1"}
        )
        assert resp.status_code == 200, username


@pytest.mark.asyncio
async def test_seed_finds_a_row_an_older_seed_stored_as_typed(db_session):
    db_session.add(User(email="Demo@Example.COM", hashed_password=hash_password("old-pw")))
    await db_session.commit()

    user, created = await seed_user(db_session, "Demo@Example.COM", "password123")
    assert not created
    assert user.email == "Demo@Example.COM"
    assert await db_session.scalar(select(func.count()).select_from(User)) == 1


@pytest.mark.asyncio
async def test_seed_rejects_a_value_that_is_not_an_email(db_session):
    with pytest.raises(ValueError):
        await seed_user(db_session, "not-an-email", "password123")
    assert await db_session.scalar(select(func.count()).select_from(User)) == 0

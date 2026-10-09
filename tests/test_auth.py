import pytest

from app.models.user import User
from app.services.security import hash_password


@pytest.mark.asyncio
async def test_register_then_login_returns_token_pair(client):
    register_resp = await client.post(
        "/auth/register", json={"email": "alice@example.com", "password": "supersecret1"}
    )
    assert register_resp.status_code == 201
    assert register_resp.json()["email"] == "alice@example.com"

    login_resp = await client.post(
        "/auth/login",
        data={"username": "alice@example.com", "password": "supersecret1"},
    )
    assert login_resp.status_code == 200
    body = login_resp.json()
    assert "access_token" in body
    assert "refresh_token" in body


@pytest.mark.asyncio
async def test_login_accepts_the_email_exactly_as_typed_at_registration(client):
    # Registration stores the validator's normalized form (lower-cased domain); login
    # must look the typed address up the same way, or the chat page's automatic login
    # right after "create account" fails.
    typed = "Grace@Example.COM"
    register_resp = await client.post(
        "/auth/register", json={"email": typed, "password": "supersecret1"}
    )
    assert register_resp.status_code == 201

    for username in (typed, "Grace@example.com", " Grace@Example.COM "):
        resp = await client.post(
            "/auth/login", data={"username": username, "password": "supersecret1"}
        )
        assert resp.status_code == 200, username


@pytest.mark.asyncio
async def test_login_still_finds_a_row_stored_with_the_email_as_typed(client, db_session):
    # scripts/seed_demo_user.py used to store the command-line address as typed, so a
    # row can hold a spelling EmailStr would normalize differently ("Example.COM").
    db_session.add(
        User(email="Demo@Example.COM", hashed_password=hash_password("supersecret1"))
    )
    await db_session.commit()

    resp = await client.post(
        "/auth/login", data={"username": "Demo@Example.COM", "password": "supersecret1"}
    )
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_login_prefers_the_row_stored_exactly_as_typed(client, db_session):
    # A raw row and a registered (normalized) row can both exist, since registering
    # "Ivan@Example.COM" stores "Ivan@example.com". Each spelling must keep reaching
    # the row it reached before login normalized anything.
    db_session.add(User(email="Ivan@Example.COM", hashed_password=hash_password("raw-row-pw")))
    await db_session.commit()
    register_resp = await client.post(
        "/auth/register", json={"email": "Ivan@Example.COM", "password": "registered-pw"}
    )
    assert register_resp.status_code == 201
    assert register_resp.json()["email"] == "Ivan@example.com"

    for username, password, expected in (
        ("Ivan@Example.COM", "raw-row-pw", 200),
        ("Ivan@Example.COM", "registered-pw", 401),
        ("Ivan@example.com", "registered-pw", 200),
    ):
        resp = await client.post(
            "/auth/login", data={"username": username, "password": password}
        )
        assert resp.status_code == expected, (username, password)


@pytest.mark.asyncio
async def test_login_with_a_username_that_is_not_an_email_returns_401(client):
    resp = await client.post(
        "/auth/login", data={"username": "not-an-email", "password": "supersecret1"}
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_register_duplicate_email_conflicts(client):
    payload = {"email": "bob@example.com", "password": "supersecret1"}
    first = await client.post("/auth/register", json=payload)
    assert first.status_code == 201

    second = await client.post("/auth/register", json=payload)
    assert second.status_code == 409


@pytest.mark.asyncio
async def test_login_wrong_password_returns_401(client):
    await client.post(
        "/auth/register", json={"email": "carol@example.com", "password": "supersecret1"}
    )
    resp = await client.post(
        "/auth/login",
        data={"username": "carol@example.com", "password": "wrong-password"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "password",
    [
        "short1",  # under 8 characters
        "가" * 25,  # 25 characters but 75 bytes in UTF-8, over bcrypt's 72-byte input limit
    ],
)
async def test_register_rejects_passwords_outside_the_rules(client, password):
    resp = await client.post(
        "/auth/register", json={"email": "dave@example.com", "password": password}
    )
    assert resp.status_code == 422
    assert resp.json()["detail"][0]["loc"][-1] == "password"


@pytest.mark.asyncio
async def test_a_72_byte_password_registers_and_logs_in(client):
    password = "가" * 24  # exactly 72 bytes
    register_resp = await client.post(
        "/auth/register", json={"email": "erin@example.com", "password": password}
    )
    assert register_resp.status_code == 201

    login_resp = await client.post(
        "/auth/login", data={"username": "erin@example.com", "password": password}
    )
    assert login_resp.status_code == 200


@pytest.mark.asyncio
@pytest.mark.parametrize("email", ["not-an-email", "nul\x00@example.com"])
async def test_register_rejects_a_malformed_email(client, email):
    resp = await client.post("/auth/register", json={"email": email, "password": "supersecret1"})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_login_with_a_nul_character_in_the_username_returns_401(client):
    # No stored address holds U+0000 (registration refuses it), and PostgreSQL rejects it
    # in a query parameter, so the lookup must not reach the database (it used to be a 500).
    await client.post(
        "/auth/register", json={"email": "gina@example.com", "password": "supersecret1"}
    )
    resp = await client.post(
        "/auth/login", data={"username": "gina@example.com\x00", "password": "supersecret1"}
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_login_with_an_overlong_password_is_rejected_not_a_server_error(client):
    # bcrypt 5 raises on input over 72 bytes; login must answer 401, not crash with 500.
    await client.post(
        "/auth/register", json={"email": "frank@example.com", "password": "supersecret1"}
    )
    resp = await client.post(
        "/auth/login", data={"username": "frank@example.com", "password": "x" * 100}
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_requires_auth(client):
    resp = await client.get("/auth/me")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_returns_current_user(authed_client):
    resp = await authed_client.get("/auth/me")
    assert resp.status_code == 200
    assert resp.json()["email"] == "test@example.com"

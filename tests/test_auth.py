import pytest


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
async def test_register_rejects_a_malformed_email(client):
    resp = await client.post(
        "/auth/register", json={"email": "not-an-email", "password": "supersecret1"}
    )
    assert resp.status_code == 422


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

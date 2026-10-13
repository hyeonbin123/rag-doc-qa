# [테스트 묶음] 가입·로그인·현재 사용자 API(app/routers/auth.py)의 통합 테스트. 실제 테스트 DB와 앱을
# conftest의 client로 호출한다.
# [왜 중요한가] 여기 있는 테스트 대부분은 실제로 났던 버그의 회귀 방지다: 72바이트를 넘는 비밀번호에서
# bcrypt 5가 오류를 내 500이 나던 것(커밋 b9bdf04), 가입은 이메일을 정규화해 저장하는데 로그인은 그대로 찾아
# 401이 나던 것(커밋 bdece46), 예전 시드 스크립트가 입력 그대로 저장한 계정이 로그인 못 하던 것(커밋
# 1d520fb), NUL 문자가 든 입력이 500을 내던 것(ZAP 1차 스캔, docs/security-scan.md, 커밋 55002dc).

import pytest

# 예전 시드 스크립트가 만든 '입력 그대로 저장된 행'을 테스트에서 직접 넣으려고 사용자 모델과 해시 함수를
# 가져온다.
from app.models.user import User
from app.services.security import hash_password


# 기본 흐름: 가입은 201과 저장된 이메일을, 로그인은 access·refresh 토큰 쌍을 돌려준다.
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


# 가입 때 입력한 대소문자 그대로, 정규화된 형태로, 앞뒤 공백이 붙은 형태로 로그인해도 모두 성공해야 한다. 채팅
# 화면은 가입 직후 같은 입력으로 자동 로그인하므로 이게 깨지면 가입 직후 401이 난다(커밋 bdece46).
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


# 정규화 전 형태('Example.COM')로 저장된 예전 행도 같은 문자열로 로그인할 수 있어야 한다. 로그인 조회에
# 정규화를 넣은 뒤 이 경우가 401이 됐던 문제를 막는다(커밋 1d520fb).
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


# 같은 주소의 원문 행과 정규화 행이 둘 다 있을 때, 각 철자가 정규화 도입 전에 닿던 행으로 가는지 확인한다.
# 입력 그대로 저장된 행이 우선이므로 'Ivan@Example.COM' + 가입 때 비밀번호는 401이다.
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


# 이메일 형식이 아닌 사용자 이름은 정규화에서 실패해도 500이 아니라 401(로그인 실패)이어야 한다.
@pytest.mark.asyncio
async def test_login_with_a_username_that_is_not_an_email_returns_401(client):
    resp = await client.post(
        "/auth/login", data={"username": "not-an-email", "password": "supersecret1"}
    )
    assert resp.status_code == 401


# 같은 이메일로 두 번 가입하면 409 Conflict.
@pytest.mark.asyncio
async def test_register_duplicate_email_conflicts(client):
    payload = {"email": "bob@example.com", "password": "supersecret1"}
    first = await client.post("/auth/register", json=payload)
    assert first.status_code == 201

    second = await client.post("/auth/register", json=payload)
    assert second.status_code == 409


# 틀린 비밀번호는 401.
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


# 가입 비밀번호 규칙: 8자 미만이거나 UTF-8로 72바이트를 넘으면 422이고, 오류 위치(loc) 마지막 값이
# 'password'여야 한다. 채팅 화면이 이 값으로 비밀번호 규칙 위반과 이메일 오류를 구분해 안내한다(커밋
# b9bdf04). 한글 25자는 글자 수로는 규칙 안이지만 75바이트라 걸린다.
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


# 경계값: 정확히 72바이트(한글 24자)는 가입과 로그인 모두 성공해야 한다.
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


# 형식이 틀린 이메일과 NUL 문자가 든 이메일은 가입에서 422. NUL은 PostgreSQL이 문자열에 저장하지 못해 예전에는
# 500이 났다(커밋 55002dc, ZAP 1차 지적).
@pytest.mark.asyncio
@pytest.mark.parametrize("email", ["not-an-email", "nul\x00@example.com"])
async def test_register_rejects_a_malformed_email(client, email):
    resp = await client.post("/auth/register", json={"email": email, "password": "supersecret1"})
    assert resp.status_code == 422


# 로그인 이름에 NUL이 있으면 DB까지 가지 않고 401이어야 한다(조회 함수가 미리 걸러 냄).
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


# 72바이트를 넘는 비밀번호로 로그인하면 bcrypt를 부르지 않고 401(틀린 비밀번호로 취급)이어야 한다. 예전에는
# bcrypt 5의 ValueError로 500이 났다(커밋 b9bdf04).
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


# 토큰 없이 /auth/me를 부르면 401, conftest의 authed_client(가입·로그인한 사용자)로 부르면 그 사용자의
# 이메일을 돌려준다.
@pytest.mark.asyncio
async def test_me_requires_auth(client):
    resp = await client.get("/auth/me")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_returns_current_user(authed_client):
    resp = await authed_client.get("/auth/me")
    assert resp.status_code == 200
    assert resp.json()["email"] == "test@example.com"

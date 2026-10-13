# [테스트 묶음] 데모 계정 시드 스크립트(scripts/seed_demo_user.py)의 seed_user를 실제 테스트 DB로 검증한다.
# [왜 중요한가] 예전 스크립트는 입력한 주소를 그대로 저장해, 로그인이 정규화된 주소로 찾게 바뀐 뒤 그 계정이
# 로그인하지 못했다(커밋 1d520fb). 지금은 가입과 같은 형태로 저장하고, 예전 행이 있으면 새로 만들지 않아야
# 한다.
# [import] SQLAlchemy func·select는 사용자 행 수를 직접 세는 데 쓴다.

import pytest
from pydantic import ValidationError
from sqlalchemy import func, select

# 예전 형식의 행을 직접 넣을 사용자 모델과 해시 함수, 테스트 대상 seed_user.
from app.models.user import User
from app.services.security import hash_password
from scripts.seed_demo_user import seed_user


# 시드한 주소가 가입과 같은 정규화 형태(도메인만 소문자)로 저장되고, 그 뒤 같은 문자열로 가입하면 409(이미
# 있음), 입력 그대로와 정규화 형태 둘 다로 로그인이 되는지 확인한다. 시드 계정이 가입한 계정과 똑같이 동작해야
# 한다.
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


# 예전 스크립트가 입력 그대로 저장한 행이 있으면, 같은 주소로 다시 시드해도 새 계정을 만들지 않고 그 행을
# 돌려준다(행 수 1). 같은 사람의 계정이 두 개 생기지 않게 한다.
@pytest.mark.asyncio
async def test_seed_finds_a_row_an_older_seed_stored_as_typed(db_session):
    db_session.add(User(email="Demo@Example.COM", hashed_password=hash_password("old-pw")))
    await db_session.commit()

    user, created = await seed_user(db_session, "Demo@Example.COM", "password123")
    assert not created
    assert user.email == "Demo@Example.COM"
    assert await db_session.scalar(select(func.count()).select_from(User)) == 1


# 이메일 형식이 아니면 ValueError로 끝나고 DB에 아무 행도 남기지 않는다.
@pytest.mark.asyncio
async def test_seed_rejects_a_value_that_is_not_an_email(db_session):
    with pytest.raises(ValueError):
        await seed_user(db_session, "not-an-email", "password123")
    assert await db_session.scalar(select(func.count()).select_from(User)) == 0


# 비밀번호도 가입 API와 같은 규칙으로 DB를 건드리기 전에 거부한다: 8자 미만(예전에는 그대로 계정이 생김)과
# UTF-8 72바이트 초과(한글 25자 = 75바이트, 예전에는 bcrypt 5의 ValueError traceback). pydantic
# ValidationError인지 보는 것은 bcrypt가 내는 일반 ValueError와 구분하려는 것이다.
@pytest.mark.asyncio
@pytest.mark.parametrize("password", ["short", "가" * 25])
async def test_seed_refuses_a_password_registration_refuses(db_session, password):
    with pytest.raises(ValidationError):
        await seed_user(db_session, "ivan@example.com", password)
    assert await db_session.scalar(select(func.count()).select_from(User)) == 0

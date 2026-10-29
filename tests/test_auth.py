# [테스트 묶음] 가입·로그인·현재 사용자 API(app/routers/auth.py)의 통합 테스트. 실제 테스트 DB와 앱을
# conftest의 client로 호출한다.
# [왜 중요한가] 여기 있는 테스트 대부분은 실제로 났던 버그의 회귀 방지다: 72바이트를 넘는 비밀번호에서
# bcrypt 5가 오류를 내 500이 나던 것(커밋 b9bdf04), 가입은 이메일을 정규화해 저장하는데 로그인은 그대로 찾아
# 401이 나던 것(커밋 bdece46), 예전 시드 스크립트가 입력 그대로 저장한 계정이 로그인 못 하던 것(커밋
# 1d520fb), NUL 문자가 든 입력이 500을 내던 것(ZAP 1차 스캔, docs/security-scan.md, 커밋 55002dc), sub가
# UUID가 아닌 서명 토큰과 동시 가입 경쟁의 진 쪽이 500을 내던 것. 맨 아래 묶음은 인증 감사 로그(이메일은
# 지문만, 비밀번호·토큰 값은 남기지 않음)를 고정한다.

import hashlib
import json
import logging
import uuid
from datetime import UTC, datetime, timedelta

# jwt: 앱의 비밀키로 '이 앱은 발급하지 않는 모양'의 토큰(sub가 UUID가 아님)을 직접 서명할 때만 쓴다.
import jwt
import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker

# 예전 시드 스크립트가 만든 '입력 그대로 저장된 행'을 테스트에서 직접 넣으려고 사용자 모델과 해시 함수를
# 가져온다. security 모듈은 앱이 쓰는 비밀키·알고리즘(security.settings)과 갱신 토큰 발급 함수를 쓰려고
# 가져온다.
from app.models.user import User
from app.services import security
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
    # 가입은 검증기가 정규화한 형태(도메인 소문자)로 저장하므로, 로그인도 입력한 주소를 같은 방식으로 찾아야
    # 한다. 그렇지 않으면 채팅 화면에서 "계정 만들기" 직후의 자동 로그인이 실패한다.
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
    # scripts/seed_demo_user.py는 예전에 명령행으로 받은 주소를 입력 그대로 저장했으므로, EmailStr이 다르게
    # 정규화할 철자("Example.COM")를 담은 행이 있을 수 있다.
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
    # 원래 철자 행과 가입으로 만든(정규화된) 행이 함께 있을 수 있다. "Ivan@Example.COM"으로 가입하면
    # "Ivan@example.com"이 저장되기 때문이다. 각 철자는 로그인이 정규화를 하기 전에 닿던 행에 계속 닿아야
    # 한다.
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
        "short1",  # 8자 미만
        "가" * 25,  # 25자지만 UTF-8로 75바이트라 bcrypt 입력 한도 72바이트를 넘는다
    ],
)
async def test_register_rejects_passwords_outside_the_rules(client, password):
    resp = await client.post(
        "/auth/register", json={"email": "dave@example.com", "password": password}
    )
    assert resp.status_code == 422
    assert resp.json()["detail"][0]["loc"][-1] == "password"


# 422 본문은 제출한 값을 되돌려 주지 않는다. pydantic 오류 항목의 input(제출값)에는 규칙에 걸린 비밀번호
# 원문이나 본문 전체가 그대로 들어 있었다. 화면이 쓰는 loc·type과 msg·ctx(예: min_length)는 그대로 남는다.
# 한글 비밀번호는 ASCII JSON 안에서 유니코드 이스케이프로 나오므로, 파싱한 값에서도 찾는다.
@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("password", "error_type"),
    [
        ("S3cret!", "string_too_short"),  # 8자 미만
        ("가" * 25, "value_error"),  # 25자, UTF-8로 75바이트라 72바이트를 넘는다
    ],
)
async def test_a_rejected_password_is_not_echoed_back_in_the_422(client, password, error_type):
    resp = await client.post("/auth/register", json={"email": "dave@example.com", "password": password})

    assert resp.status_code == 422
    [error] = resp.json()["detail"]
    assert error["loc"] == ["body", "password"]
    assert error["type"] == error_type
    assert error["msg"]
    assert "ctx" in error
    assert "input" not in error and "url" not in error
    assert password not in resp.text
    assert password not in json.dumps(resp.json(), ensure_ascii=False)


# 필드가 빠졌을 때(missing)의 input은 요청 본문 전체이고, /auth/refresh에서 키 이름을 틀리면 보낸 갱신 토큰이
# 그 안에 들어 있었다. 두 경우 모두 본문의 값이 422 응답에 나오지 않아야 한다.
@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("path", "payload", "secret", "field"),
    [
        ("/auth/register", {"email": "dave@example.com"}, "dave@example.com", "password"),
        (
            "/auth/refresh",
            {"refreshToken": "refresh-token-value-from-the-client"},
            "refresh-token-value-from-the-client",
            "refresh_token",
        ),
    ],
)
async def test_a_missing_field_422_does_not_echo_the_request_body(client, path, payload, secret, field):
    resp = await client.post(path, json=payload)

    assert resp.status_code == 422
    [error] = resp.json()["detail"]
    assert error["type"] == "missing"
    assert error["loc"] == ["body", field]
    assert secret not in resp.text


# 경계값: 정확히 72바이트(한글 24자)는 가입과 로그인 모두 성공해야 한다.
@pytest.mark.asyncio
async def test_a_72_byte_password_registers_and_logs_in(client):
    password = "가" * 24  # 정확히 72바이트
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
    # 저장된 주소에는 U+0000이 없고(가입이 거부한다) PostgreSQL은 질의 파라미터에 든 U+0000을 거부하므로,
    # 조회가 DB까지 가면 안 된다(예전에는 500이 났다).
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
    # bcrypt 5는 72바이트를 넘는 입력에서 예외를 낸다. 로그인은 500으로 죽지 않고 401로 답해야 한다.
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


# 서명은 맞지만 sub가 UUID가 아닌 토큰은 접근 토큰 자리(/auth/me)와 갱신 토큰 자리(/auth/refresh) 모두 500이
# 아니라 평소의 401이어야 한다. 앱이 쓰는 비밀키로 직접 서명해 만든다(이 앱은 이런 토큰을 발급하지 않는다).
@pytest.mark.asyncio
@pytest.mark.parametrize("token_type", ["access", "refresh"])
async def test_a_signed_token_with_a_non_uuid_subject_is_a_401_not_a_500(client, token_type):
    now = datetime.now(UTC)
    token = jwt.encode(
        {"sub": "not-a-uuid", "type": token_type, "iat": now, "exp": now + timedelta(minutes=5)},
        security.settings.jwt_secret_key,
        algorithm=security.settings.jwt_algorithm,
    )

    if token_type == "access":
        resp = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 401
        assert resp.json()["detail"] == "Could not validate credentials"
        assert resp.headers["www-authenticate"] == "Bearer"
    else:
        resp = await client.post("/auth/refresh", json={"refresh_token": token})
        assert resp.status_code == 401
        assert resp.json()["detail"] == "Invalid refresh token"


# 동시 가입 경쟁: 중복 확인을 통과한 직후 다른 요청이 같은 주소로 가입을 먼저 끝내면, 진 쪽의 삽입은
# users.email 유일 제약에 걸린다. 예전에는 IntegrityError가 그대로 올라가 500이었다. 이제 먼저 확인에 걸렸을
# 때와 같은 409이고, 세션을 rollback하므로 같은 세션으로 이어지는 요청도 정상이다(rollback을 빠뜨리면 다음
# 요청이 PendingRollbackError로 실패한다). 경쟁은 라우터의 첫 db.scalar(중복 확인)가 '없음'을 돌려준 직후
# 다른 세션(다른 요청 역할)으로 같은 주소의 행을 넣고 commit해 만든다.
@pytest.mark.asyncio
async def test_a_registration_that_loses_the_race_is_a_409_and_the_session_stays_usable(
    client, db_engine, db_session, monkeypatch
):
    email = "race@example.com"
    real_scalar = db_session.scalar
    calls = 0

    async def check_then_let_the_competitor_register_first(*args, **kwargs):
        nonlocal calls
        calls += 1
        result = await real_scalar(*args, **kwargs)
        if calls == 1:  # 라우터의 중복 확인이 '없음'을 본 직후 경쟁자가 같은 주소로 가입을 끝낸다
            async with async_sessionmaker(db_engine)() as competitor:
                competitor.add(User(email=email, hashed_password=hash_password("winner-pw-1")))
                await competitor.commit()
        return result

    monkeypatch.setattr(db_session, "scalar", check_then_let_the_competitor_register_first)

    resp = await client.post("/auth/register", json={"email": email, "password": "loser-pw-12"})

    assert resp.status_code == 409
    assert resp.json()["detail"] == "Email already registered"
    # 같은 세션으로 이어지는 요청: 이긴 쪽 비밀번호로 로그인되고, 다른 주소의 가입도 된다.
    login = await client.post("/auth/login", data={"username": email, "password": "winner-pw-1"})
    assert login.status_code == 200
    after = await client.post(
        "/auth/register", json={"email": "after-race@example.com", "password": "supersecret1"}
    )
    assert after.status_code == 201
    assert await db_session.scalar(select(func.count()).select_from(User).where(User.email == email)) == 1


# 가입 commit의 IntegrityError라도 다시 확인했을 때 그 주소가 없으면(주소 중복이 아닌 다른 무결성 오류) 409로
# 숨기지 않고 원래 예외를 그대로 올린다. 새로 넣은 분기의 회귀 방지다(고치기 전 코드도 예외를 그대로 올렸다).
@pytest.mark.asyncio
async def test_an_integrity_error_that_is_not_a_taken_email_is_not_reported_as_a_409(
    client, db_session, monkeypatch
):
    async def commit_failing_on_another_constraint():
        raise IntegrityError("INSERT INTO users ...", params=None, orig=Exception("another constraint"))

    monkeypatch.setattr(db_session, "commit", commit_failing_on_another_constraint)

    with pytest.raises(IntegrityError):
        await client.post("/auth/register", json={"email": "other@example.com", "password": "supersecret1"})


# --- 인증 감사 로그 (app/routers/auth.py) ---


# 감사 로그의 이메일 지문을 문서에 적힌 공식(앞뒤 공백 제거·소문자의 sha256 16진수 앞 8자)대로 따로 계산한다.
# 구현의 email_fingerprint를 쓰지 않아, 공식이 바뀌면 이 테스트가 잡는다.
def _fingerprint(email: str) -> str:
    return hashlib.sha256(email.strip().lower().encode("utf-8")).hexdigest()[:8]


# 인증 라우터 로거의 기록만 고른다(다른 로거의 기록이 섞여도 단언이 흔들리지 않게).
def _auth_records(caplog) -> list[tuple[int, str]]:
    return [(r.levelno, r.getMessage()) for r in caplog.records if r.name == "app.routers.auth"]


# 로그인 시도는 결과마다 한 줄씩 남는다: 틀린 비밀번호·없는 주소는 WARNING(reason으로 구분), 성공은 INFO.
# 이메일은 지문으로만, 클라이언트 주소는 그대로(테스트 클라이언트는 127.0.0.1) 적고, 주소 원문·비밀번호·발급한
# 토큰은 로그 어디에도 없어야 한다. 'carol@Example.COM'은 가입한 'carol@example.com'으로 정규화돼 찾아지므로
# 같은 지문이다.
@pytest.mark.asyncio
async def test_login_attempts_are_logged_without_the_address_or_the_password(client, caplog):
    registered = await client.post(
        "/auth/register", json={"email": "carol@example.com", "password": "supersecret1"}
    )
    user_id = registered.json()["id"]

    with caplog.at_level(logging.INFO, logger="app.routers.auth"):
        wrong = await client.post(
            "/auth/login", data={"username": "carol@Example.COM", "password": "wrong-password"}
        )
        unknown = await client.post(
            "/auth/login", data={"username": "nobody@example.com", "password": "whatever-pw"}
        )
        ok = await client.post(
            "/auth/login", data={"username": "carol@example.com", "password": "supersecret1"}
        )

    assert (wrong.status_code, unknown.status_code, ok.status_code) == (401, 401, 200)
    carol = _fingerprint("carol@example.com")
    assert _auth_records(caplog) == [
        (
            logging.WARNING,
            f"login failed reason=wrong_password user={user_id} email={carol} client=127.0.0.1",
        ),
        (
            logging.WARNING,
            f"login failed reason=unknown_email email={_fingerprint('nobody@example.com')} client=127.0.0.1",
        ),
        (logging.INFO, f"login succeeded user={user_id} email={carol} client=127.0.0.1"),
    ]
    tokens = ok.json()
    for secret in ("carol", "nobody", "@", "wrong-password", "whatever-pw", "supersecret1"):
        assert secret not in caplog.text, secret
    assert tokens["access_token"] not in caplog.text
    assert tokens["refresh_token"] not in caplog.text


# 가입 성공은 INFO, 이미 있는 주소로 다시 가입하면 WARNING 한 줄이다. 주소 원문과 비밀번호는 남기지 않는다.
@pytest.mark.asyncio
async def test_registrations_are_logged_without_the_address_or_the_password(client, caplog):
    with caplog.at_level(logging.INFO, logger="app.routers.auth"):
        first = await client.post(
            "/auth/register", json={"email": "dana@example.com", "password": "supersecret1"}
        )
        again = await client.post(
            "/auth/register", json={"email": "dana@example.com", "password": "another-pw-1"}
        )

    assert (first.status_code, again.status_code) == (201, 409)
    dana = _fingerprint("dana@example.com")
    assert _auth_records(caplog) == [
        (logging.INFO, f"user registered user={first.json()['id']} email={dana} client=127.0.0.1"),
        (logging.WARNING, f"registration rejected reason=email_taken email={dana} client=127.0.0.1"),
    ]
    for secret in ("dana", "@", "supersecret1", "another-pw-1"):
        assert secret not in caplog.text, secret


# 거부된 갱신은 이유와 함께 WARNING 한 줄이다: 토큰 자체가 무효(서명·모양이 틀림, 접근 토큰을 갱신 자리에
# 씀)면 decode_token의 고정 문구를 detail로, 서명은 맞지만 사용자가 없거나 비활성이면 그 사용자 id를 적는다.
# 보낸 토큰 값은 로그 어디에도 없어야 한다.
@pytest.mark.asyncio
async def test_rejected_refreshes_are_logged_without_the_token(authed_client, db_session, caplog):
    access = authed_client.headers["Authorization"].removeprefix("Bearer ")
    user = await db_session.scalar(select(User).where(User.email == "test@example.com"))
    ghost_id = uuid.uuid4()
    ghost_token = security.create_refresh_token(ghost_id)
    inactive_token = security.create_refresh_token(user.id)
    user.is_active = False
    await db_session.commit()

    with caplog.at_level(logging.INFO, logger="app.routers.auth"):
        responses = [
            await authed_client.post("/auth/refresh", json={"refresh_token": token})
            for token in ("not-a-real-refresh-token", access, ghost_token, inactive_token)
        ]

    assert [resp.status_code for resp in responses] == [401, 401, 401, 401]
    assert _auth_records(caplog) == [
        (
            logging.WARNING,
            "refresh rejected reason=invalid_token detail='could not validate token' client=127.0.0.1",
        ),
        (
            logging.WARNING,
            "refresh rejected reason=invalid_token detail='expected a refresh token' client=127.0.0.1",
        ),
        (logging.WARNING, f"refresh rejected reason=unknown_user user={ghost_id} client=127.0.0.1"),
        (logging.WARNING, f"refresh rejected reason=inactive_user user={user.id} client=127.0.0.1"),
    ]
    for secret in ("not-a-real-refresh-token", access, ghost_token, inactive_token):
        assert secret not in caplog.text

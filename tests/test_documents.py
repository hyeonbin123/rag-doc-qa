# [테스트 묶음] 문서 조회·관리자 적재 API(app/routers/documents.py)의 입력 검증 테스트. 잘못된 입력이 500(서버
# 오류)이 아니라 422·404로 끝나는지 확인한다. 끝부분은 관리자 토큰 검사(공개 예시 값 거부, 상수 시간 비교)다.
# [왜 중요한가] 문서 id를 UUID로 받기 전에는 형식이 틀린 id가 500을 냈다(커밋 9e7d6eb). NUL
# 문자 거부는 ZAP 1차 스캔 뒤 PostgreSQL이 저장할 수 없는 문자열을 422로 막은 변경(커밋 55002dc)을 적재
# API에도 고정한다.

import secrets
import uuid

import pytest

# 관리자 토큰 검사 의존성을 테스트에서 통과시키고, 적재 함수를 바꿔 끼우려고 라우터 모듈을 가져온다. 설정
# 의존성(get_settings)은 관리자 토큰만 바꾼 설정으로 갈아 끼우고, 가짜 적재는 IngestOutcome을 돌려준다.
from app.config import get_settings
from app.dependencies import require_admin_token
from app.main import app
from app.routers import documents
from app.services.ingestion import IngestOutcome


# UUID가 아닌 문서 id는 DB 조회 전에 경로 검증에서 422로 막혀야 한다.
@pytest.mark.asyncio
async def test_a_malformed_document_id_is_rejected_not_a_server_error(client):
    resp = await client.get("/documents/not-a-uuid")
    assert resp.status_code == 422


# 형식은 맞지만 없는 문서 id는 404.
@pytest.mark.asyncio
async def test_an_unknown_document_id_is_not_found(client):
    resp = await client.get(f"/documents/{uuid.uuid4()}")
    assert resp.status_code == 404


# 적재 요청의 commit_sha에 NUL이 있으면 요청 검증 단계에서 422로 막혀 적재가 시작되지 않아야 한다. 적재가
# 실제로 불리면 실패하도록 run_ingestion을 바꿔 끼우고(GitHub·임베딩 없이 검사), 관리자 토큰 검사는 이
# 테스트에서만 통과시킨다. 교체는 client 픽스처가 끝날 때 함께 지워진다.
@pytest.mark.asyncio
async def test_ingest_rejects_a_nul_character_in_the_commit(client, monkeypatch):
    # 커밋 값은 모든 문서 행에 저장되는데, PostgreSQL text는 U+0000을 담을 수 없다.
    async def must_not_run(*args, **kwargs):
        raise AssertionError("ingestion ran")

    monkeypatch.setattr(documents, "run_ingestion", must_not_run)
    app.dependency_overrides[require_admin_token] = lambda: None

    resp = await client.post("/admin/documents/ingest", json={"commit_sha": "abc\x00def"})

    assert resp.status_code == 422
    assert resp.json()["detail"][0]["loc"] == ["body", "commit_sha"]


# --- 관리자 토큰 (app/dependencies.py의 require_admin_token) ---


# 관리자 토큰을 정한 설정. 다른 설정은 테스트 환경 그대로 두고 admin_ingest_token만 바꾼다.
def _with_admin_token(token: str):
    settings = get_settings().model_copy(update={"admin_ingest_token": token})
    app.dependency_overrides[get_settings] = lambda: settings


# 적재가 실제로 불렸는지 기록하는 가짜 적재. GitHub·임베딩 없이 토큰 검사만 본다.
@pytest.fixture
def fake_ingestion(monkeypatch):
    calls = []

    async def fake_run_ingestion(*args, **kwargs):
        calls.append(kwargs)
        return IngestOutcome(
            documents_processed=0,
            documents_deleted=0,
            chunks_created=0,
            chunks_updated=0,
            chunks_skipped=0,
            elapsed_ms=0,
            commit_sha="deadbeef",
        )

    monkeypatch.setattr(documents, "run_ingestion", fake_run_ingestion)
    return calls


# 설정한 토큰과 같은 헤더면 적재가 돈다.
@pytest.mark.asyncio
async def test_ingest_runs_with_the_configured_admin_token(client, fake_ingestion):
    _with_admin_token("a-real-secret-token")

    resp = await client.post(
        "/admin/documents/ingest", json={}, headers={"X-Admin-Token": "a-real-secret-token"}
    )

    assert resp.status_code == 200
    assert len(fake_ingestion) == 1


# 다른 토큰이면 403이고 적재는 돌지 않는다. ASCII 밖 바이트가 든 헤더(latin-1로 풀림)도 500이 아니라 403이다.
@pytest.mark.asyncio
@pytest.mark.parametrize("header", [b"a-real-secret-tokeN", b"caf\xe9"])
async def test_ingest_rejects_any_other_admin_token(client, fake_ingestion, header):
    _with_admin_token("a-real-secret-token")

    resp = await client.post("/admin/documents/ingest", json={}, headers={"X-Admin-Token": header})

    assert resp.status_code == 403
    assert fake_ingestion == []


# 토큰이 비어 있거나(설정 기본값) 예전 공개 예시 값이면, 같은 값을 헤더로 보내도 관리자 적재가 꺼져 있어야
# 한다. 예전에는 .env.example을 그대로 복사한 서버에서 누구나 그 예시 값으로 적재(문서 삭제 포함)를 돌릴 수
# 있었고, 빈 토큰에는 빈 헤더가 통과했다.
@pytest.mark.asyncio
@pytest.mark.parametrize("token", ["", "change-me-admin-token"])
async def test_ingest_is_disabled_while_the_admin_token_is_a_placeholder(client, fake_ingestion, token):
    _with_admin_token(token)

    resp = await client.post("/admin/documents/ingest", json={}, headers={"X-Admin-Token": token})

    assert resp.status_code == 403
    assert "disabled" in resp.json()["detail"]
    assert fake_ingestion == []


# 토큰 비교는 secrets.compare_digest(상수 시간 비교)로 한다. 일반 비교(!=)는 앞에서부터 다른 글자를 만나면
# 멈추므로, 응답 시간으로 토큰을 한 글자씩 맞혀 갈 여지가 생긴다.
@pytest.mark.asyncio
async def test_the_admin_token_is_compared_in_constant_time(client, fake_ingestion, monkeypatch):
    compared = []
    real_compare_digest = secrets.compare_digest

    def spy(a, b):
        compared.append((a, b))
        return real_compare_digest(a, b)

    monkeypatch.setattr(secrets, "compare_digest", spy)
    _with_admin_token("a-real-secret-token")

    resp = await client.post(
        "/admin/documents/ingest", json={}, headers={"X-Admin-Token": "a-real-secret-token"}
    )

    assert resp.status_code == 200
    assert compared == [(b"a-real-secret-token", b"a-real-secret-token")]

# [테스트 묶음] 문서 조회·관리자 적재 API(app/routers/documents.py)의 입력 검증 테스트. 잘못된 입력이 500(서버
# 오류)이 아니라 422·404로 끝나는지 확인한다.
# [왜 중요한가] 문서 id를 UUID로 받기 전에는 형식이 틀린 id가 500을 냈다(커밋 9e7d6eb). NUL
# 문자 거부는 ZAP 1차 스캔 뒤 PostgreSQL이 저장할 수 없는 문자열을 422로 막은 변경(커밋 55002dc)을 적재
# API에도 고정한다.

import uuid

import pytest

# 관리자 토큰 검사 의존성을 테스트에서 통과시키고, 적재 함수를 바꿔 끼우려고 라우터 모듈을 가져온다.
from app.dependencies import require_admin_token
from app.main import app
from app.routers import documents


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
    # The commit is stored on every document; PostgreSQL text cannot hold U+0000.
    async def must_not_run(*args, **kwargs):
        raise AssertionError("ingestion ran")

    monkeypatch.setattr(documents, "run_ingestion", must_not_run)
    app.dependency_overrides[require_admin_token] = lambda: None

    resp = await client.post("/admin/documents/ingest", json={"commit_sha": "abc\x00def"})

    assert resp.status_code == 422
    assert resp.json()["detail"][0]["loc"] == ["body", "commit_sha"]

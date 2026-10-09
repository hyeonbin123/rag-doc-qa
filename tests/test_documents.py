import uuid

import pytest

from app.dependencies import require_admin_token
from app.main import app
from app.routers import documents


@pytest.mark.asyncio
async def test_a_malformed_document_id_is_rejected_not_a_server_error(client):
    resp = await client.get("/documents/not-a-uuid")
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_an_unknown_document_id_is_not_found(client):
    resp = await client.get(f"/documents/{uuid.uuid4()}")
    assert resp.status_code == 404


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

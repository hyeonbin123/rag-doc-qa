import uuid

import pytest


@pytest.mark.asyncio
async def test_a_malformed_document_id_is_rejected_not_a_server_error(client):
    resp = await client.get("/documents/not-a-uuid")
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_an_unknown_document_id_is_not_found(client):
    resp = await client.get(f"/documents/{uuid.uuid4()}")
    assert resp.status_code == 404

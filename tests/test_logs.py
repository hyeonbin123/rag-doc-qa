import uuid

import pytest


@pytest.mark.asyncio
async def test_a_malformed_log_id_is_rejected_not_a_server_error(authed_client):
    resp = await authed_client.get("/logs/not-a-uuid")
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_an_unknown_log_id_is_not_found(authed_client):
    resp = await authed_client.get(f"/logs/{uuid.uuid4()}")
    assert resp.status_code == 404


@pytest.mark.asyncio
@pytest.mark.parametrize("query", ["limit=-1", "offset=-1", "limit=0", "limit=101"])
async def test_paging_outside_the_bounds_is_rejected(authed_client, query):
    # Negative values used to reach Postgres, which rejects them: a 500.
    resp = await authed_client.get(f"/logs?{query}")
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_paging_within_the_bounds_works(authed_client):
    resp = await authed_client.get("/logs?limit=100&offset=0")
    assert resp.status_code == 200
    assert resp.json() == []

import pytest


@pytest.mark.asyncio
async def test_index_serves_the_chat_page(client):
    resp = await client.get("/")

    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/html")
    assert "FastAPI 문서에 물어보기" in resp.text


@pytest.mark.asyncio
async def test_health_reports_retrieval_mode_and_generation_model(client):
    resp = await client.get("/health")

    body = resp.json()
    assert body["db"] == "ok"
    assert body["retrieval_mode"] in {"dense", "hybrid", "rerank"}
    assert body["generation_model"]


@pytest.mark.asyncio
async def test_register_conflict_is_documented_in_openapi(client):
    spec = (await client.get("/openapi.json")).json()

    assert "409" in spec["paths"]["/auth/register"]["post"]["responses"]

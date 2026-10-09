import re

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


@pytest.mark.asyncio
async def test_the_chat_page_allows_only_same_origin_code_and_no_framing(client):
    resp = await client.get("/")

    csp = resp.headers["content-security-policy"]
    assert "default-src 'self'" in csp
    assert "frame-ancestors 'none'" in csp
    assert "unsafe-inline" not in csp and "sha256-" not in csp
    assert resp.headers["x-frame-options"] == "DENY"
    assert resp.headers["x-content-type-options"] == "nosniff"


@pytest.mark.asyncio
async def test_the_chat_page_keeps_its_code_in_files_the_policy_allows(client):
    # The policy allows no inline code, so a <script> or <style> block, a style attribute or
    # an event-handler attribute in the page would be blocked by the browser.
    html = (await client.get("/")).text

    assert re.search(r"<script(?![^>]*\ssrc=)[^>]*>", html) is None
    assert "<style" not in html
    assert re.search(r"\s(style|on[a-z]+)=", html) is None
    files = re.findall(r'(?:src|href)="(/static/[^"]+)"', html)
    assert sorted(files) == ["/static/chat.css", "/static/chat.js"]
    for path in files:
        resp = await client.get(path)
        assert resp.status_code == 200
        assert resp.headers["x-content-type-options"] == "nosniff"


@pytest.mark.asyncio
@pytest.mark.parametrize("path", ["/health", "/openapi.json", "/documents/not-a-uuid", "/no-such-page"])
async def test_api_responses_carry_the_security_headers(client, path):
    resp = await client.get(path)

    assert resp.headers["x-content-type-options"] == "nosniff"
    assert resp.headers["x-frame-options"] == "DENY"
    assert "frame-ancestors 'none'" in resp.headers["content-security-policy"]


@pytest.mark.asyncio
@pytest.mark.parametrize("path", ["/docs", "/redoc"])
async def test_the_docs_pages_may_load_their_cdn_files_but_not_be_framed(client, path):
    resp = await client.get(path)

    csp = resp.headers["content-security-policy"]
    hosts = set(re.findall(r'(?:src|href)="(https://[^/"]+)', resp.text))
    assert hosts  # FastAPI's page loads Swagger UI / ReDoc from a CDN
    assert all(host in csp for host in hosts), hosts
    assert "frame-ancestors 'none'" in csp
    assert resp.headers["x-frame-options"] == "DENY"

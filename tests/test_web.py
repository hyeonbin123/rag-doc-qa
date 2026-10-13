# [테스트 묶음] 채팅 화면(/), 헬스 체크, OpenAPI 문서, 그리고 모든 응답의 보안 헤더(app/main.py)를 확인하는
# 테스트.
# [왜 중요한가] ZAP 1차 스캔에서 채팅 화면에 CSP와 클릭재킹 방지 헤더가 없다는 Medium 2개와 nosniff 헤더가
# 없다는 Low가 나왔고, 고친 뒤 2차 스캔에서 사라졌다(docs/security-scan.md, 커밋 ce7a847). 헤더와 '인라인 코드
# 없는 페이지'가 다시 깨지지 않게 고정한다.
# [import] re는 HTML에서 스크립트·스타일·이벤트 속성과 외부 파일 주소를 찾는 데 쓴다.

import re

import pytest


# 루트(/)가 채팅 화면 HTML을 돌려주는지 화면 제목 문구로 확인한다.
@pytest.mark.asyncio
async def test_index_serves_the_chat_page(client):
    resp = await client.get("/")

    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/html")
    assert "FastAPI 문서에 물어보기" in resp.text


# /health가 DB 연결 상태와 지금 검색 모드, 생성 모델 이름을 알려 주는지 확인한다.
@pytest.mark.asyncio
async def test_health_reports_retrieval_mode_and_generation_model(client):
    resp = await client.get("/health")

    body = resp.json()
    assert body["db"] == "ok"
    assert body["retrieval_mode"] in {"dense", "hybrid", "rerank"}
    assert body["generation_model"]


# 가입 API의 409(이미 있는 이메일) 응답이 OpenAPI 문서에 적혀 있는지 확인한다. Swagger UI를 보는 사람이 가능한
# 응답을 알 수 있게 한다.
@pytest.mark.asyncio
async def test_register_conflict_is_documented_in_openapi(client):
    spec = (await client.get("/openapi.json")).json()

    assert "409" in spec["paths"]["/auth/register"]["post"]["responses"]


# 채팅 화면의 CSP가 같은 출처의 파일만 허용하고(default-src 'self'), 인라인 코드 예외(unsafe-inline, 해시)가
# 없으며, 다른 사이트의 프레임 안에 넣지 못하게 하는지(frame-ancestors 'none', X-Frame-Options DENY),
# nosniff가 붙는지 확인한다.
@pytest.mark.asyncio
async def test_the_chat_page_allows_only_same_origin_code_and_no_framing(client):
    resp = await client.get("/")

    csp = resp.headers["content-security-policy"]
    assert "default-src 'self'" in csp
    assert "frame-ancestors 'none'" in csp
    assert "unsafe-inline" not in csp and "sha256-" not in csp
    assert resp.headers["x-frame-options"] == "DENY"
    assert resp.headers["x-content-type-options"] == "nosniff"


# CSP가 인라인 코드를 막으므로 페이지 안에 src 없는 <script>, <style> 블록, style·on* 속성이 하나도 없어야
# 한다(있으면 브라우저가 막아 화면이 깨진다). 페이지가 불러오는 파일은 /static/chat.css와 /static/chat.js
# 둘뿐이고, 둘 다 200과 nosniff로 응답하는지 확인한다.
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


# HTML이 아닌 API 응답(JSON, 422, 404 포함)에도 같은 보안 헤더가 붙는지 경로 네 개로 확인한다. ZAP 1차 스캔의
# nosniff 지적은 JSON 응답 5곳이었다.
@pytest.mark.asyncio
@pytest.mark.parametrize("path", ["/health", "/openapi.json", "/documents/not-a-uuid", "/no-such-page"])
async def test_api_responses_carry_the_security_headers(client, path):
    resp = await client.get(path)

    assert resp.headers["x-content-type-options"] == "nosniff"
    assert resp.headers["x-frame-options"] == "DENY"
    assert "frame-ancestors 'none'" in resp.headers["content-security-policy"]


# FastAPI가 만드는 /docs·/redoc은 CDN에서 Swagger UI·ReDoc 파일을 불러오므로, 페이지가 실제로 쓰는 외부
# 호스트가 모두 CSP에 들어 있어야 화면이 뜬다. 느슨한 정책이어도 프레임 금지는 유지되는지 확인한다.
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

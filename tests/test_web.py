# [테스트 묶음] 채팅 화면(/), 헬스 체크, OpenAPI 문서, 그리고 모든 응답의 보안 헤더(app/main.py)를 확인하는
# 테스트.
# [왜 중요한가] ZAP 1차 스캔에서 채팅 화면에 CSP와 클릭재킹 방지 헤더가 없다는 Medium 2개와 nosniff 헤더가
# 없다는 Low가 나왔고, 고친 뒤 2차 스캔에서 사라졌다(docs/security-scan.md, 커밋 ce7a847). 헤더와 '인라인 코드
# 없는 페이지'가 다시 깨지지 않게 고정한다.
# [import] re는 HTML에서 스크립트·스타일·이벤트 속성과 외부 파일 주소를 찾는 데 쓴다. generation은 생성기 장애
# code 목록(503 응답의 detail.code)을 가져오는 데 쓴다. importlib·config·main_module·Settings·httpx는
# APP_ENV=production으로 만든 앱(문서 페이지를 끈 앱)을 따로 세워 볼 때 쓴다.

import importlib
import re

import pytest
from httpx import ASGITransport, AsyncClient

import app.config as config
import app.main as main_module
from app.config import Settings
from app.services import generation


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
    assert hosts  # FastAPI 문서 페이지는 Swagger UI / ReDoc을 CDN에서 불러온다
    assert all(host in csp for host in hosts), hosts
    assert "frame-ancestors 'none'" in csp
    assert resp.headers["x-frame-options"] == "DENY"


# 기본(APP_ENV=development) 앱에서는 문서 페이지 세 경로(Swagger UI, 그 OAuth2 리다이렉트, ReDoc)가 느슨한
# 문서용 정책을 받는다. 꺼진 경로를 뜻하는 None이 목록에 섞이지 않는다.
def test_development_mode_keeps_the_docs_pages_under_the_docs_policy():
    assert main_module.DOCS_PATHS == {"/docs", "/docs/oauth2-redirect", "/redoc"}
    assert None not in main_module.DOCS_PATHS


# APP_ENV=production으로 만든 앱. app.main은 import할 때 설정을 읽어 앱을 만들므로, 설정 조회 함수를
# production 설정을 돌려주는 함수로 잠시 바꾸고 모듈을 다시 실행(importlib.reload)한다. 끝나면 모듈의 이름
# 공간을 다시 실행하기 전 그대로 되돌려, 다른 테스트가 쓰는 원래 앱 객체(conftest의 app)와 모듈 전역
# (DOCS_PATHS 등)이 처음 상태로 돌아가게 한다. get_settings의 캐시와 다른 모듈이 읽어 둔 설정은 건드리지
# 않는다.
@pytest.fixture
def production_app():
    namespace = vars(main_module)
    saved = dict(namespace)
    production = Settings(database_url="x", jwt_secret_key="k" * 64, app_env="production", _env_file=None)
    try:
        with pytest.MonkeyPatch.context() as patch:
            patch.setattr(config, "get_settings", lambda: production)
            importlib.reload(main_module)
        yield main_module.app
    finally:
        namespace.clear()
        namespace.update(saved)


# production에서는 /docs·/docs/oauth2-redirect·/redoc을 아예 만들지 않아 404이고, 그 404에도 엄격한 앱 정책
# (APP_CSP)이 붙는다. 문서 페이지는 CDN 스크립트와 인라인 코드를 허용해야 하는데, 채팅 화면과 같은 출처라 그
# 스크립트가 sessionStorage의 접근 토큰을 읽을 수 있기 때문이다. /openapi.json은 남긴다(ZAP 스캔
# zap/automation.yaml이 이 주소로 API 목록을 읽는다).
@pytest.mark.asyncio
async def test_production_mode_turns_off_the_docs_pages_but_keeps_the_openapi_schema(production_app):
    assert production_app.docs_url is None and production_app.redoc_url is None
    assert main_module.DOCS_PATHS == frozenset()

    transport = ASGITransport(app=production_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        for path in ("/docs", "/docs/oauth2-redirect", "/redoc"):
            resp = await client.get(path)
            assert resp.status_code == 404, path
            assert resp.headers["content-security-policy"] == main_module.APP_CSP, path
        spec = await client.get("/openapi.json")

    assert spec.status_code == 200
    assert "/query/ask" in spec.json()["paths"]


# /query/ask의 503(생성기 장애)은 detail.code로 원인을 알리고, 채팅 화면(app/web/static/chat.js)이 code마다
# 다른 안내(모델 만들기, Ollama 실행 확인, 잠시 뒤 다시)를 보인다. 서버가 code를 더하거나 이름을 바꾸고
# 화면을 빠뜨리면 화면은 원인을 모르는 일반 문구로 돌아가므로, 서버의 code 목록이 화면 스크립트에 모두 있는지
# 본다.
@pytest.mark.asyncio
async def test_the_chat_page_explains_every_generator_error_code(client):
    script = (await client.get("/static/chat.js")).text

    assert generation.GENERATOR_ERROR_MESSAGES
    for code in generation.GENERATOR_ERROR_MESSAGES:
        assert f"'{code}'" in script, code

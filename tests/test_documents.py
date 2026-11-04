# [테스트 묶음] 문서 조회·관리자 적재 API(app/routers/documents.py)의 입력 검증 테스트. 잘못된 입력이 500(서버
# 오류)이 아니라 422·404·409로 끝나는지 확인한다. 끝부분은 관리자 토큰 검사(공개 예시 값 거부, 상수 시간
# 비교)다.
# [왜 중요한가] 문서 id를 UUID로 받기 전에는 형식이 틀린 id가 500을 냈다(커밋 9e7d6eb). NUL
# 문자 거부는 ZAP 1차 스캔 뒤 PostgreSQL이 저장할 수 없는 문자열을 422로 막은 변경(커밋 55002dc)을 적재
# API에도 고정한다. 적재 요청의 limit·commit_sha 범위·형식 검사는 2026-10-29에 더했다: 그 전에는 limit 0이
# '전체 적재 + 사라진 문서 삭제', 음수가 '뒤 n개를 빼고 처리'가 됐고, 'master' 같은 ref 이름이 문서 행의
# source_commit_sha에 그대로 저장됐다(이제 적재가 GitHub에 물어 40자 SHA로 바꾼다, tests/test_ingestion.py).

import logging
import secrets
import uuid

# httpx: GitHub 응답을 MockTransport로 흉내 내고, 500 응답을 받으려고 앱 예외를 올리지 않는 클라이언트를 따로
# 만든다. SQLAlchemy: 오류로 끝난 적재가 문서·청크 행을 남기지 않았는지 센다.
import httpx
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import func, select

# 관리자 토큰 검사 의존성을 테스트에서 통과시키고, 적재 함수를 바꿔 끼우려고 라우터 모듈을 가져온다. 설정
# 의존성(get_settings)은 관리자 토큰만 바꾼 설정으로 갈아 끼우고, 가짜 적재는 IngestOutcome을 돌려준다. 적재
# 모듈(ingestion)은 '적재가 이미 진행 중' 예외를 참조하고, GitHub 클라이언트(github_client)와 기본 ref 설정을
# 바꿔 끼우는 데 쓴다. 문서·청크 모델은 남은 행을 세는 데 쓴다.
from app.config import get_settings
from app.dependencies import require_admin_token
from app.main import app
from app.models.chunk import Chunk
from app.models.document import Document
from app.routers import documents
from app.services import ingestion
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


# --- 적재 요청 본문 검증 (app/schemas/document.py의 IngestRequest) ---


# 적재가 실제로 불리면 실패하는 가짜 run_ingestion. 요청 검증(422)이 적재를 시작하기 전에 막는지 보는 테스트가
# 쓴다(GitHub·임베딩 없이 검사). 관리자 토큰 검사는 그 테스트에서만 통과시키고, 교체는 client 픽스처가 끝날 때
# 함께 지워진다.
async def must_not_run(*args, **kwargs):
    raise AssertionError("ingestion ran")


# 적재 요청의 commit_sha에 NUL이 있으면 요청 검증 단계에서 422로 막혀 적재가 시작되지 않아야 한다.
@pytest.mark.asyncio
async def test_ingest_rejects_a_nul_character_in_the_commit(client, monkeypatch):
    # 커밋 값은 모든 문서 행에 저장되는데, PostgreSQL text는 U+0000을 담을 수 없다.
    monkeypatch.setattr(documents, "run_ingestion", must_not_run)
    app.dependency_overrides[require_admin_token] = lambda: None

    resp = await client.post("/admin/documents/ingest", json={"commit_sha": "abc\x00def"})

    assert resp.status_code == 422
    assert resp.json()["detail"][0]["loc"] == ["body", "commit_sha"]


# limit은 1 이상이어야 한다. 예전에는 `int | None`이라 0과 음수가 그대로 들어갔고, 적재 코드가 limit의
# 참·거짓만 봐서 0은 'limit 없음'(약 8분짜리 전체 적재 + 트리에 없는 문서 삭제), 음수는 paths[:-n](뒤 n개를
# 빼고 처리, 삭제 단계 생략)이 됐다. '시험용으로 조금만' 넣으려던 요청이 의도와 반대로 도는 셈이다.
@pytest.mark.asyncio
@pytest.mark.parametrize("limit", [0, -1])
async def test_ingest_rejects_a_limit_below_one(client, monkeypatch, limit):
    monkeypatch.setattr(documents, "run_ingestion", must_not_run)
    app.dependency_overrides[require_admin_token] = lambda: None

    resp = await client.post("/admin/documents/ingest", json={"limit": limit})

    assert resp.status_code == 422
    assert resp.json()["detail"][0]["loc"] == ["body", "limit"]


# commit_sha로 받는 ref는 영숫자·'.'·'_'·'-' 조각을 '/'로 이은 꼴, 1~100자, '..' 없음, '.'으로 시작하는 조각
# 없음만 통과한다. 값이 GitHub URL 경로에 그대로 들어가므로 '..'·'.' 세그먼트는 다른 API 경로를 가리키게
# 되고(httpx가 점 세그먼트를 정규화해 '.' 하나는 커밋 목록 경로 .../commits가 된다), 공백·'?'·'#'은 경로를
# 끊는다. 이 검사는 보안 통제가 아니라 정확성 검사다(신뢰 경계는 관리자 토큰, 40자 16진수만 받아도 포크
# 네트워크 커밋은 못 막음, app/services/ingestion.py 주석).
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "ref",
    [
        "a..b",
        "../x",
        ".",
        "./x",
        "a/./b",
        "x/.",
        ".hidden",
        "x?y",
        "x#y",
        "x y",
        "a" * 101,
        "/master",
        "master/",
        "a//b",
        "",
    ],
)
async def test_ingest_rejects_an_unsafe_commit_ref(client, monkeypatch, ref):
    monkeypatch.setattr(documents, "run_ingestion", must_not_run)
    app.dependency_overrides[require_admin_token] = lambda: None

    resp = await client.post("/admin/documents/ingest", json={"commit_sha": ref})

    assert resp.status_code == 422
    assert resp.json()["detail"][0]["loc"] == ["body", "commit_sha"]


# 브랜치 이름, 태그, 짧은 SHA, 40자 SHA, 슬래시가 든 브랜치는 모두 통과해 적재 함수에 그대로 넘어가야
# 한다(SHA로 바꾸는 일은 적재 함수가 GitHub에 물어 한다). `--commit master` 같은 기존 사용법을 막지 않는지
# 고정한다.
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "ref",
    ["master", "50113da", "50113da16fec53b66b80d75e80a89296de4fa5a5", "v0.100.0", "release/1.0", "fix_x-1.2"],
)
async def test_ingest_accepts_branch_tag_and_sha_refs(client, fake_ingestion, ref):
    app.dependency_overrides[require_admin_token] = lambda: None

    resp = await client.post("/admin/documents/ingest", json={"commit_sha": ref})

    assert resp.status_code == 200
    assert fake_ingestion[0]["commit_sha"] == ref


# 같은 DB에서 다른 적재(이 API의 다른 요청이나 CLI)가 진행 중이면 적재 함수가 IngestionAlreadyRunning을 내고,
# 라우터는 이를 409로 바꿔야 한다. 예전에는 두 적재가 함께 돌다가 늦은 쪽이 먼저 쪽의 commit을 몇 분 기다린 뒤
# 유일 제약 위반 500으로 끝났다. 잠금 자체는 tests/test_ingestion.py가 실제 DB로 확인한다.
@pytest.mark.asyncio
async def test_ingest_reports_a_running_ingestion_as_a_conflict(client, monkeypatch):
    async def already_running(*args, **kwargs):
        raise ingestion.IngestionAlreadyRunning("another ingestion is already running")

    monkeypatch.setattr(documents, "run_ingestion", already_running)
    app.dependency_overrides[require_admin_token] = lambda: None

    resp = await client.post("/admin/documents/ingest", json={})

    assert resp.status_code == 409
    assert resp.json()["detail"] == "ingestion already running"


# --- GitHub가 모르는 ref·GitHub 장애 (2026-11-05) ---
# 아래 테스트는 적재 함수를 바꾸지 않고 GitHub 쪽 HTTP만 httpx.MockTransport로 흉내
# 낸다(ingestion.github_client 자리). 그래서 ref 해석부터 라우터의 오류 응답까지 실제 코드가 돈다. 예전에는
# GitHub가 모르는 ref(commits API의 404)와 GitHub 장애(5xx, 요청 한도 초과, 연결 실패·시간 초과)가 모두
# 처리되지 않은 예외라 500이 됐다.


# 가짜 GitHub의 응답 하나를 만드는 함수들. 응답 객체를 테스트끼리 함께 쓰지 않으려고 요청마다 새로 만든다.
# answer(code, ...)는 그 상태 코드의 응답을, fail(예외 클래스)는 그 요청에서 httpx 요청 오류(연결 실패·시간
# 초과 흉내)를 낸다.
def answer(code: int, **kwargs):
    return lambda request: httpx.Response(code, **kwargs)


def fail(error_type: type[httpx.RequestError]):
    def raise_error(request: httpx.Request) -> httpx.Response:
        raise error_type("simulated failure", request=request)

    return raise_error


COMMIT_OK = answer(200, json={"sha": "c0ffee" + "0" * 34})
TREE_OK = answer(200, json={"tree": [{"path": "docs/en/docs/a.md", "type": "blob"}], "truncated": False})


# 적재가 쓰는 GitHub 클라이언트를 가짜로 바꾼다. 커밋 조회(.../commits/{ref})는 commits, 트리 목록
# (.../git/trees/...)은 tree, 그 밖(raw 원문)은 raw가 답한다. 받은 요청의 URL을 차례로 모아 돌려준다.
def serve_github(monkeypatch, commits, tree=None, raw=None) -> list[str]:
    requests: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(str(request.url))
        if "/commits/" in request.url.path:
            return commits(request)
        if "/git/trees/" in request.url.path:
            return tree(request)
        return raw(request)

    monkeypatch.setattr(
        ingestion, "github_client", lambda: httpx.AsyncClient(transport=httpx.MockTransport(handler))
    )
    return requests


# 적재 테이블에 행이 하나도 없는지 센다(오류로 끝난 적재가 DB에 아무것도 쓰지 않았는지).
async def stored_rows(db_session) -> tuple[int, int]:
    documents = await db_session.scalar(select(func.count()).select_from(Document))
    chunks = await db_session.scalar(select(func.count()).select_from(Chunk))
    return documents, chunks


# 요청이 준 ref를 GitHub가 모르면(commits API 404, 커밋으로 풀 수 없는 값의 422) 422로 답한다. 오류 항목은
# 다른 검증 오류(위 형식 검사)와 같은 꼴이라 loc이 body.commit_sha를 가리키고, 보낸 값은 되돌려 주지 않는다.
# 트리와 원문은 받지 않고 DB에도 쓰지 않는다.
@pytest.mark.asyncio
@pytest.mark.parametrize("github_status", [404, 422])
async def test_ingest_reports_a_ref_github_does_not_know_as_unprocessable(
    client, db_session, monkeypatch, github_status
):
    requests = serve_github(monkeypatch, commits=answer(github_status, json={"message": "No commit found"}))
    app.dependency_overrides[require_admin_token] = lambda: None

    resp = await client.post("/admin/documents/ingest", json={"commit_sha": "no-such-branch"})

    assert resp.status_code == 422
    assert resp.json()["detail"] == [
        {"type": "unknown_docs_ref", "loc": ["body", "commit_sha"], "msg": "GitHub does not know this ref"}
    ]
    assert len(requests) == 1
    assert await stored_rows(db_session) == (0, 0)


# GitHub에 닿지 못하거나(연결 실패·시간 초과) GitHub가 오류 상태로 답하면(5xx, 요청 한도 초과의 403) 커밋
# 해석·트리 목록·원문 받기 어느 단계든 502로 답하고 DB에는 아무것도 쓰지 않는다. 원인은 응답에 싣지 않고 서버
# 로그 한 줄(WARNING)에만 남겨, 운영자가 '우리 버그(500)'와 '상류 장애(502)'를 가를 수 있게 한다.
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "commits, tree, raw",
    [
        (answer(503), None, None),
        (fail(httpx.ConnectError), None, None),
        (COMMIT_OK, answer(403, json={"message": "API rate limit exceeded"}), None),
        (COMMIT_OK, TREE_OK, fail(httpx.ReadTimeout)),
        (COMMIT_OK, TREE_OK, answer(500)),
    ],
    ids=["commit-503", "commit-connect-error", "tree-rate-limited", "raw-timeout", "raw-500"],
)
async def test_ingest_reports_an_unreachable_github_as_a_bad_gateway(
    client, db_session, monkeypatch, caplog, commits, tree, raw
):
    serve_github(monkeypatch, commits, tree, raw)
    app.dependency_overrides[require_admin_token] = lambda: None

    with caplog.at_level(logging.WARNING, logger="app.routers.documents"):
        resp = await client.post("/admin/documents/ingest", json={"commit_sha": "master"})

    assert resp.status_code == 502
    assert resp.json()["detail"] == "docs source unavailable"
    assert "docs source unavailable" in caplog.text
    assert await stored_rows(db_session) == (0, 0)


# 요청이 ref를 주지 않았는데 서버 기본 ref(설정 FASTAPI_DOCS_COMMIT_SHA)를 GitHub가 모르면, 요청을 고쳐서 풀릴
# 일이 아닌 서버 설정 오류라 422가 아니라 500으로 남긴다(본문은 다른 예기치 않은 오류와 같은 'Internal Server
# Error', 원인은 서버 로그의 트레이스백). 기본 테스트 클라이언트는 앱 예외를 테스트로 올리므로
# raise_app_exceptions=False 클라이언트를 따로 만든다(의존성 교체는 client 픽스처의 것을 그대로 쓴다).
@pytest.mark.asyncio
async def test_an_unknown_configured_ref_stays_a_server_error(client, db_session, monkeypatch):
    settings = get_settings().model_copy(update={"fastapi_docs_commit_sha": "no-such-branch"})
    monkeypatch.setattr(ingestion, "get_settings", lambda: settings)
    requests = serve_github(monkeypatch, commits=answer(404, json={"message": "No commit found"}))
    app.dependency_overrides[require_admin_token] = lambda: None
    transport = ASGITransport(app=app, raise_app_exceptions=False)

    async with AsyncClient(transport=transport, base_url="http://test") as raw_client:
        resp = await raw_client.post("/admin/documents/ingest", json={})

    assert resp.status_code == 500
    assert resp.text == "Internal Server Error"
    assert requests == [f"{ingestion.GITHUB_API}/repos/{ingestion.REPO}/commits/no-such-branch"]
    assert await stored_rows(db_session) == (0, 0)


# 적재 API의 422(검증 오류와 GitHub가 모르는 ref)와 502(GitHub 장애)가 OpenAPI 문서에 적혀 있는지 본다. 422를
# 따로 적어도 다른 경로의 자동 422와 같은 검증 오류 스키마(HTTPValidationError)를 가리켜야, 문서를 보는 쪽이
# 같은 꼴로 처리할 수 있다.
@pytest.mark.asyncio
async def test_ingest_errors_are_documented_in_openapi(client):
    spec = (await client.get("/openapi.json")).json()

    responses = spec["paths"]["/admin/documents/ingest"]["post"]["responses"]
    assert {"409", "422", "502"} <= set(responses)
    schema = responses["422"]["content"]["application/json"]["schema"]
    assert schema == {"$ref": "#/components/schemas/HTTPValidationError"}
    assert "HTTPValidationError" in spec["components"]["schemas"]


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

"""GitHub에서 FastAPI 문서를 받아 청킹·임베딩하고 Postgres에 넣거나 갱신(upsert)한다.

내용 해시로 멱등하다: 바뀌지 않은 파일은 건너뛰고, 바뀐 파일은 청크를 통째로 교체한다. 그래서 문서가
갱신된 뒤 적재를 다시 돌려도 실제로 바뀐 것만 다시 계산한다. 전체 적재(limit 없음)는 적재한 언어의 문서
중 트리 목록에 더는 없는 것, 즉 상류에서 지워지거나 이름이 바뀌었거나 새로 제외된 페이지도 지운다. 그러면
코퍼스가 그 커밋 시점의 문서와 똑같아진다.
"""

# [파일 역할] FastAPI 공식 문서(GitHub tiangolo/fastapi의 docs/en/docs/, docs/ko/docs/)를 받아 청킹·임베딩하고
# documents·chunks 테이블에 넣는 적재 파이프라인.
# [흐름] limit 검사 → 적재 잠금(pg_try_advisory_xact_lock, dry run은 제외) → GitHub 클라이언트 만들기(스레드
# 풀) → ref를 40자 커밋 SHA로 해석 → GitHub 트리에서 언어별 마크다운 경로 목록 → 원문을 최대 8개씩 동시에 받기
# → 문서마다 해시 비교(같으면 건너뜀) → 바뀐 문서는 기존 청크를 지우고 청킹(스레드 풀)·임베딩(모델 스레드)해
# 다시 넣기 → 전체 적재면 트리에서 사라진 문서 지우기 → 커밋(잠금도 풀림) → 바뀐 것이 있으면 VACUUM (ANALYZE).
# [설계 이유]
# - 위 docstring처럼 내용 해시로 멱등하게 만들어, 다시 돌려도 바뀐 문서만 처리한다. 해시에 청커 버전과 임베딩
#   모델 식별자를 넣은 이유는 아래 주석과 docs/experiments.md v1→v3, v8에 있다.
# - 임베딩은 몇 분 걸리는 CPU 작업이라 모델 스레드(run_model)에서, 청킹과 GitHub 클라이언트 생성(CA 번들
#   읽기)은 Starlette 스레드 풀(run_in_threadpool)에서 돌려 API 서버가 적재 중에도 응답한다.
# - 적재 대상은 늘 커밋 SHA로 고정한다. ref 이름(브랜치·태그·짧은 SHA)을 받아도 GitHub에 물어 40자 SHA로
#   바꾸고, 아무것도 주지 않으면 측정에 쓴 문서 스냅숏(DOCS_SNAPSHOT_COMMIT)을 쓴다. 그래서 문서 행의
#   source_commit_sha가 늘 실제 커밋을 가리키고, README 절차를 그대로 따른 적재가 측정과 같은 코퍼스가 된다.
# - 한 DB에서 적재는 한 번에 하나만 돈다(어드바이저리 잠금). 관리자 API와 CLI가 겹쳐 같은 문서를 둘 다 새로
#   넣다가 한쪽이 몇 분 뒤 유일 제약 오류로 끝나는 일을 막는다.
# [연결] 관리자 API(app/routers/documents.py)와 CLI(scripts/ingest_fastapi_docs.py)가 run_ingestion을,
# scripts/fetch_docs.py가 github_client·resolve_commit_sha·list_doc_paths를 쓴다.

from __future__ import annotations

import asyncio
import hashlib
import re
import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass

# httpx: GitHub API와 raw 파일을 비동기로 받는다. run_in_threadpool: 동기 함수(청킹, GitHub 클라이언트 생성)를
# Starlette의 기본 스레드 풀에서 돌린다. SQLAlchemy: 문서 조회·청크 삭제·사라진 문서 삭제 질의와 어드바이저리
# 잠금 SQL. 앱 내부:
# 설정(기본 적재 ref), 모델, ref 형식 검사, 청커, 임베딩 서비스 타입, 모델 스레드, 지원 언어.
import httpx
from fastapi.concurrency import run_in_threadpool
from sqlalchemy import and_, delete, func, or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.chunk import Chunk
from app.models.document import Document
from app.schemas.text import validate_git_ref
from app.services.chunking import (
    CHUNKER_VERSION,
    build_embedding_text,
    chunk_markdown,
    strip_heading_anchor,
)
from app.services.embedding import EmbeddingService
from app.services.inference import run_model
from app.services.language import SUPPORTED_LANGUAGES

# GitHub REST API(커밋·트리 조회)와 raw 파일 주소, 대상 저장소. DOC_LANGUAGES는 기본 적재 언어(지원 언어
# 전체).
GITHUB_API = "https://api.github.com"
RAW_BASE = "https://raw.githubusercontent.com"
REPO = "tiangolo/fastapi"
DOC_LANGUAGES: tuple[str, ...] = SUPPORTED_LANGUAGES
# 문서가 아니라 사이트 장식에 해당하는 페이지: MkDocs가 AI 도움을 받은 번역 페이지에 붙이는 안내문이다.
SKIPPED_PAGES = {"translation-banner.md"}
# 원문 파일을 동시에 받는 최대 개수. 수백 개 문서를 한꺼번에 요청하지 않도록 세마포어로 제한한다.
MAX_CONCURRENT_FETCHES = 8
# 측정에 쓴 문서 스냅숏: tiangolo/fastapi 커밋 50113da. docs/experiments.md의 복제 DB·재적재 명령(v12 이후)과
# 본 DB의 277개 문서가 모두 이 커밋이고, README의 수치는 이 코퍼스에서 잰 것이다. commit_sha도 설정
# FASTAPI_DOCS_COMMIT_SHA도 없을 때의 기본값이다. 기본을 master의 최신 커밋으로 두면(2026-10-29 전 동작)
# README 절차를 그대로 따른 적재가 측정과 다른 코퍼스가 되고 전체 적재의 삭제 동기화까지 일어나므로 재현 쪽을
# 기본으로 둔다. 최신 문서는 --commit master(또는 설정에 master)로 명시해서 받는다.
DOCS_SNAPSHOT_COMMIT = "50113da16fec53b66b80d75e80a89296de4fa5a5"
# GitHub commits API가 돌려주는 커밋 SHA의 형식. 문서 행의 source_commit_sha(String(40))과 트리·원문 URL이 이
# 형식을 가정한다.
_COMMIT_SHA_RE = re.compile(r"[0-9a-f]{40}")
# 적재 잠금에 쓰는 PostgreSQL 어드바이저리 잠금 키(bigint). 'rag-doc-qa/ingestion'의 SHA-256 앞 8바이트를
# 빅엔디언 부호 있는 64비트 정수로 읽은 고정 상수다(int.from_bytes(digest[:8], "big", signed=True)). 같은 DB를
# 쓰는 모든 프로세스(관리자 API, CLI)가 같은 키를 쓰므로 한 DB에서 적재는 한 번에 하나만 돈다. 이 DB를 함께
# 쓰는 다른 코드가 같은 키로 어드바이저리 잠금을 쓰지 않는 한 충돌하지 않는다(지금은 이 잠금 하나뿐이다).
INGESTION_LOCK_KEY = 2126143313622324131


# 같은 DB에서 다른 적재(관리자 API의 다른 요청이나 CLI 프로세스)가 진행 중이라 이번 적재를 시작하지 않았을
# 때의 예외. 라우터는 409로, CLI는 종료 코드 1로 바꾼다.
class IngestionAlreadyRunning(RuntimeError):
    """같은 DB에서 다른 적재가 적재 잠금(PostgreSQL 어드바이저리 잠금)을 쥐고 있다."""


# GitHub에서 문서를 받지 못해 적재를 멈췄을 때의 예외 셋(2026-11-05). 셋 다 네트워크 단계(커밋 해석 → 트리
# 목록 → 원문 받기)에서만 나고 그 뒤의 DB 단계보다 앞이라, 이 예외로 끝난 적재는 DB에 아무것도 쓰지 않는다
# (잡아 둔 적재 잠금은 세션이 닫히며 롤백과 함께 풀린다). 예전에는 httpx 예외가 그대로 올라가 관리자 API가
# 모두 500으로 답했다. 지금은 관리자 API(app/routers/documents.py)가 UnknownDocsRef를 422로,
# DocsSourceUnavailable을 502로 바꾸고 UnknownConfiguredDocsRef는 서버 설정 오류로 500에 남긴다. CLI
# (scripts/ingest_fastapi_docs.py)는 셋 다 한 줄 오류와 종료 코드 1로 끝낸다.
class UnknownDocsRef(RuntimeError):
    """요청이 준 ref(관리자 API의 commit_sha, CLI의 --commit)를 GitHub가 모른다.

    GitHub commits API가 404(없는 브랜치·태그·SHA)나 422(커밋으로 풀 수 없는 값)로 답한 경우다. 요청을 고치면
    풀리는 클라이언트 오류다. ref는 GitHub에 물은 ref, status_code는 GitHub의 상태 코드다.
    """

    def __init__(self, ref: str, status_code: int) -> None:
        super().__init__(f"GitHub does not know the docs ref {ref!r} (HTTP {status_code})")
        self.ref = ref
        self.status_code = status_code


class UnknownConfiguredDocsRef(RuntimeError):
    """요청이 ref를 주지 않았는데 서버 기본 ref를 GitHub가 모른다.

    기본 ref는 설정 FASTAPI_DOCS_COMMIT_SHA이고, 비어 있으면 측정 스냅숏(DOCS_SNAPSHOT_COMMIT)이다. 요청을
    고쳐서는 풀리지 않는 서버 설정 오류라 UnknownDocsRef와 따로 둔다. ref·status_code는 UnknownDocsRef와 같다.
    """

    def __init__(self, ref: str, status_code: int) -> None:
        super().__init__(
            f"GitHub does not know the default docs ref {ref!r} (HTTP {status_code}); "
            "check FASTAPI_DOCS_COMMIT_SHA"
        )
        self.ref = ref
        self.status_code = status_code


class DocsSourceUnavailable(RuntimeError):
    """GitHub(API·raw 호스트)에 닿지 못했거나 GitHub가 오류 상태로 답해 문서를 받지 못했다.

    연결 실패·시간 초과 같은 요청 오류(httpx.RequestError)와, 2xx가 아닌 응답 중 커밋 해석의 404·422(위 두
    예외)를 뺀 모든 것(5xx, 요청 한도 초과의 403·429 등)이다. 상류 장애라 잠시 뒤 다시 시도하면 될 수 있다.
    메시지에는 요청 주소와 원인이 들어간다(GitHub에는 인증 정보를 보내지 않아 주소에 비밀값이 없다).
    """


# GitHub commits API가 '그런 ref는 없다'고 답하는 상태 코드. 404는 없는 브랜치·태그·SHA, 422는 커밋으로 풀 수
# 없는 값이다.
UNKNOWN_REF_STATUSES = frozenset({404, 422})


# GitHub API·raw 파일을 받는 HTTP 클라이언트. 30초 제한, User-Agent(GitHub API는 User-Agent 없는 요청을 거부),
# 리디렉션 따라가기(저장소가 fastapi/fastapi로 옮겨져 tiangolo/fastapi 주소는 301로 안내된다). 함수로 둔 이유:
# run_ingestion과 scripts/fetch_docs.py가 같은 설정을 쓰고, 테스트가 이 함수를 MockTransport 클라이언트로 바꿔
# 네트워크 없이 ref 해석·URL 구성까지 실제 코드로 검증하기 위해서다(tests/test_ingestion.py,
# tests/test_fetch_docs.py).
def github_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(timeout=30.0, headers={"User-Agent": "rag-doc-qa-ingest"}, follow_redirects=True)


# GitHub(API·raw 호스트)에 GET 하나를 보낸다. 응답을 받지 못한 요청 오류(httpx.RequestError: 연결 실패, 시간
# 초과, 리디렉션 반복 등)는 DocsSourceUnavailable로 바꾸고, 받은 응답은 상태 코드를 보지 않고 그대로 돌려준다.
# 상태 코드의 뜻은 부르는 쪽이 정한다(커밋 해석의 404·422는 '모르는 ref', 나머지는 _require_success).
async def _github_get(client: httpx.AsyncClient, url: str, **kwargs) -> httpx.Response:
    try:
        return await client.get(url, **kwargs)
    except httpx.RequestError as exc:
        raise DocsSourceUnavailable(f"GET {url} failed: {type(exc).__name__}: {exc}") from exc


# 2xx가 아닌 응답을 DocsSourceUnavailable로 바꾼다. 예전 resp.raise_for_status()의 자리라 2xx만 통과시키는
# 기준은 같다(예전에는 httpx.HTTPStatusError가 그대로 올라가 관리자 API가 500으로 답했다).
def _require_success(resp: httpx.Response) -> httpx.Response:
    if not resp.is_success:
        raise DocsSourceUnavailable(f"GET {resp.request.url} returned HTTP {resp.status_code}")
    return resp


# 언어별 문서 폴더 경로(docs/<언어>/docs/). 경로 선택과 사라진 문서 판정에 쓴다.
def docs_prefix(language: str) -> str:
    return f"docs/{language}/docs/"


# GitHub 트리 항목 중 요청한 언어 폴더 아래의 마크다운 파일(blob, .md)만 골라 (경로, 언어)로 돌려준다.
# SKIPPED_PAGES에 있는 페이지(번역 안내 배너)는 뺀다.
def select_doc_paths(tree: list[dict], languages: Sequence[str]) -> list[tuple[str, str]]:
    """요청한 번역 언어들의 모든 마크다운 페이지를 (경로, 언어) 목록으로 돌려준다."""
    selected = []
    for item in tree:
        path = item["path"]
        if item["type"] != "blob" or not path.endswith(".md"):
            continue
        for language in languages:
            prefix = docs_prefix(language)
            if path.startswith(prefix) and path[len(prefix):] not in SKIPPED_PAGES:
                selected.append((path, language))
                break
    return selected


# commit_sha(요청 본문·--commit)가 없을 때 적재할 ref. 설정 FASTAPI_DOCS_COMMIT_SHA가 비어 있지 않으면 그
# 값(브랜치·태그·SHA. 최신 문서를 늘 받으려면 master), 비어 있으면 측정 스냅숏 DOCS_SNAPSHOT_COMMIT. 설정값도
# 같은 형식 검사를 거치고, 어긋나면 어느 설정이 문제인지 담은 ValueError를 낸다.
def default_commit_ref() -> str:
    configured = get_settings().fastapi_docs_commit_sha.strip()
    if not configured:
        return DOCS_SNAPSHOT_COMMIT
    try:
        return validate_git_ref(configured)
    except ValueError as exc:
        raise ValueError(f"FASTAPI_DOCS_COMMIT_SHA {configured!r}: {exc}") from exc


# 적재할 커밋을 정한다. commit_sha(브랜치·태그·짧은 SHA·40자 SHA)가 없으면 default_commit_ref()를 쓰고, 어느
# 경우든 GitHub의 `GET /repos/{REPO}/commits/{ref}`로 40자 커밋 SHA를 얻어 그 값만 돌려준다(이 호출은 예전
# master 기본 경로와 같은 한 번이다). 이후 트리·원문 URL과 문서 행의 source_commit_sha에 이 SHA만 쓰이므로,
# 적재 도중 상류가 바뀌어도 문서들이 서로 다른 시점으로 섞이지 않고, 'master' 같은 ref 이름이 아니라 실제
# 커밋이 기록된다(2026-10-29 전에는 값이 있으면 조회 없이 그대로 써서 ref 이름이 저장됐다).
# - ref 형식은 validate_git_ref로 먼저 검사한다(app/schemas/text.py). 이 검사는 보안 통제가 아니라 정확성
#   검사다: 신뢰 경계는 관리자 토큰이고, 40자 16진수만 받아도 GitHub가 포크 네트워크의 커밋을 원 저장소 경로로
#   내주므로 다른 내용의 주입은 막지 못한다. 막는 것은 '..' 세그먼트로 다른 API 경로를 두드리는 일(httpx가 점
#   세그먼트를 정규화한다), 저장 열(String(40))을 넘는 값이 임베딩 뒤에 실패하는 일, 시험 적재 의도와 출처
#   기록이 어긋나는 일이다.
# - GitHub가 모르는 ref(commits API의 404·422)면 트리·원문을 받기 전에 끝난다. 요청이 준 ref면 UnknownDocsRef,
#   ref를 주지 않아 기본 ref를 물은 것이면 UnknownConfiguredDocsRef다(2026-11-05 전에는 둘 다
#   httpx.HTTPStatusError가 그대로 올라갔다). GitHub에 닿지 못했거나 그 밖의 오류 상태면
#   DocsSourceUnavailable.
# - 응답이 커밋 하나(JSON 객체)가 아니거나 그 sha가 40자 16진수가 아니면 RuntimeError(저장 열과 URL이 가정하는
#   형식). JSON 배열도 같은 RuntimeError로 거부하는 이유: GitHub는 commits/{ref} 아래에 목록을 돌려주는 하위
#   경로(예: {ref}/statuses, {ref}/pulls)도 두어, 형식 검사를 통과한 ref가 그런 경로에 닿으면 커밋 대신 목록이
#   온다.
async def resolve_commit_sha(client: httpx.AsyncClient, commit_sha: str | None = None) -> str:
    ref = validate_git_ref(commit_sha) if commit_sha is not None else default_commit_ref()
    resp = await _github_get(client, f"{GITHUB_API}/repos/{REPO}/commits/{ref}")
    if resp.status_code in UNKNOWN_REF_STATUSES:
        if commit_sha is None:
            raise UnknownConfiguredDocsRef(ref, resp.status_code)
        raise UnknownDocsRef(ref, resp.status_code)
    _require_success(resp)
    data = resp.json()
    sha = data.get("sha") if isinstance(data, dict) else None
    if not isinstance(sha, str) or _COMMIT_SHA_RE.fullmatch(sha) is None:
        raise RuntimeError(f"GitHub returned an unexpected commit sha for {ref!r}: {sha!r}")
    return sha


# 커밋의 전체 파일 트리를 한 번에(recursive) 받아 문서 경로를 고른다. GitHub에 닿지 못하거나 2xx가 아닌
# 응답이면 DocsSourceUnavailable(_github_get·_require_success).
async def list_doc_paths(
    client: httpx.AsyncClient, sha: str, languages: Sequence[str]
) -> list[tuple[str, str]]:
    resp = _require_success(
        await _github_get(client, f"{GITHUB_API}/repos/{REPO}/git/trees/{sha}", params={"recursive": "1"})
    )
    data = resp.json()
    # 전체 적재는 목록에 없는 문서를 지우므로, 잘린(일부만 담긴) 목록으로 적재하면 아직 있는 페이지까지
    # 지운다. 그래서 GitHub가 트리 목록을 잘랐다고 알리면 적재를 거부한다.
    if data.get("truncated"):
        raise RuntimeError("GitHub tree listing is truncated; refusing to ingest a partial corpus")
    return select_doc_paths(data["tree"], languages)


# raw.githubusercontent.com에서 커밋 고정 경로로 원문 마크다운 한 파일을 받는다. 닿지 못하거나 2xx가 아닌
# 응답이면 DocsSourceUnavailable이다(2026-11-05 전에는 httpx 예외가 그대로 올라갔다).
async def fetch_raw_file(client: httpx.AsyncClient, sha: str, path: str) -> str:
    resp = _require_success(await _github_get(client, f"{RAW_BASE}/{REPO}/{sha}/{path}"))
    return resp.text


# 첫 번째 '# ' 헤딩을 페이지 제목으로 쓴다(앵커 ID는 지움). 없으면 경로를 제목으로 쓴다.
def extract_title(raw_text: str, fallback: str) -> str:
    for line in raw_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return strip_heading_anchor(stripped[2:].strip())
    return fallback


# 적재로 바뀌거나 지워진 청크가 남긴 죽은 행을 VACUUM으로 치우고 통계를 갱신(ANALYZE)한다. docstring의 사례는
# docs/experiments.md v8 '측정 중 겪은 문제 (d024)'에 자세히 있다. 세션의 엔진에서 따로 연결을 열어 자동 커밋
# 모드로 실행한다.
async def _vacuum_chunks(db: AsyncSession) -> None:
    """교체되거나 지워진 청크가 남긴 죽은 행을 치운다.

    바뀐 문서는 청크를 지우고 다시 넣고, 지워진 문서는 청크도 함께 지워진다. VACUUM이 죽은 행을 치우기
    전까지 HNSW 탐색은 그 행들도 훑느라 ef_search 예산을 버려질 행에 쓴다. 대량 재적재 직후 영어 튜닝용
    셋에서 맞히던 문항 하나가 빠졌다가 autovacuum이 돈 뒤 돌아온 일의 가장 그럴듯한 원인이 이것이다.
    VACUUM은 트랜잭션 안에서 돌 수 없어서 자동 커밋 연결을 쓴다.

    2026-11-03부터 앱의 벡터 검색은 정확 탐색으로 고정돼(app/services/retrieval.py의
    pin_exact_dense_search) HNSW 인덱스를 쓰지 않으므로, 위 ef_search 문제는 앱 검색에는 생기지 않는다.
    그래도 VACUUM은 죽은 행의 자리를 다시 쓸 수 있게 하고 ANALYZE로 통계를 새로 하므로, 순차 스캔과 나중에
    HNSW 인덱스를 다시 쓸 때를 위해 그대로 둔다.
    """
    async with db.bind.connect() as conn:
        conn = await conn.execution_options(isolation_level="AUTOCOMMIT")
        await conn.execute(text("VACUUM (ANALYZE) chunks"))


# 적재 잠금을 시도한다. pg_try_advisory_xact_lock은 다른 트랜잭션이 같은 키를 쥐고 있으면 기다리지 않고
# false를 돌려주므로, 그때는 IngestionAlreadyRunning을 낸다. 잠금은 현재 트랜잭션이 끝날 때(run_ingestion 끝의
# commit, 또는 오류 뒤 세션이 닫히며 하는 rollback) 저절로 풀려 따로 해제할 것이 없다. 같은 DB를 쓰는 모든
# 프로세스(관리자 API 워커, CLI)에 걸쳐 동작한다. 2026-10-29 전에는 잠금이 없어 두 적재가 함께 돌았다. 둘 다
# 아직 commit되지 않은 상대의 행을 보지 못하고 같은 문서를 쓰므로, 늦은 쪽은 같은 키를 쓰는 첫 SQL 문(새 문서
# 행 INSERT, 바뀐 문서의 청크 교체)에서 먼저 쪽이 commit할 때까지(전체 적재면 몇 분) 기다린 뒤 유일
# 제약(documents.source_path 또는 chunks의 (document_id, chunk_index)) 위반으로 끝났다(관리자 API면 500). 늦은
# 쪽의 변경은 롤백돼 데이터는 깨지지 않지만 그동안의 작업과 기다린 시간을 버린다.
async def _acquire_ingestion_lock(db: AsyncSession) -> None:
    locked = await db.scalar(
        text("SELECT pg_try_advisory_xact_lock(CAST(:key AS bigint))"), {"key": INGESTION_LOCK_KEY}
    )
    if not locked:
        raise IngestionAlreadyRunning(
            "another ingestion is already running on this database; wait for it to finish and retry"
        )


# 적재 결과 집계. chunks_skipped는 이름과 달리 해시가 같아 건너뛴 '문서' 수다(문서마다 1씩 더한다).
# documents_processed는 새로 넣거나 갱신한 문서 수(dry_run이면 그럴 문서 수).
@dataclass
class IngestOutcome:
    documents_processed: int
    documents_deleted: int
    chunks_created: int
    chunks_updated: int
    chunks_skipped: int
    elapsed_ms: int
    commit_sha: str


# 적재 본체.
# - embedder_for: 언어 → 임베딩 서비스. 문서 언어마다 그 언어의 모델로 임베딩한다.
# - commit_sha: 적재할 ref(브랜치·태그·SHA). 없으면 default_commit_ref(). 어느 쪽이든 resolve_commit_sha가
#   40자 SHA로 바꾼다.
# - limit: 앞에서 n개 경로만 처리(시험용), 1 이상. 이때는 사라진 문서 삭제를 하지 않는다. 0·음수는
#   ValueError다: 2026-10-29 전에는 참·거짓으로 판정해 0이 '전체 적재 + 삭제', 음수가 paths[:-n](뒤 n개 제외,
#   삭제 생략)이 됐다.
# - dry_run: DB를 바꾸지 않고 처리·삭제될 개수만 센다(잠금도 잡지 않는다).
# - languages: 적재할 언어(CLI의 --languages). 삭제도 이 언어 범위 안에서만 한다.
# 같은 DB에서 다른 적재가 진행 중이면(어드바이저리 잠금) 아무 일도 하지 않고 IngestionAlreadyRunning을 낸다.
# GitHub가 ref를 모르거나 GitHub에서 문서를 받지 못하면 네트워크 단계에서 UnknownDocsRef,
# UnknownConfiguredDocsRef, DocsSourceUnavailable 중 하나로 끝나고, 그때까지 DB에는 아무것도 쓰지 않았다.
async def run_ingestion(
    db: AsyncSession,
    embedder_for: Callable[[str], EmbeddingService],
    commit_sha: str | None = None,
    limit: int | None = None,
    dry_run: bool = False,
    languages: Sequence[str] = DOC_LANGUAGES,
) -> IngestOutcome:
    if limit is not None and limit < 1:
        raise ValueError("limit must be at least 1 (omit it to ingest every page)")

    start = time.perf_counter()
    documents_processed = 0
    documents_deleted = 0
    chunks_created = 0
    chunks_updated = 0
    chunks_skipped = 0

    # 잠금: 관리자 API의 다른 요청이나 CLI 프로세스가 같은 DB에 적재 중이면 바로 거부한다. 트랜잭션 잠금이라
    # 맨 끝의 commit(또는 오류로 세션이 닫힐 때의 rollback)과 함께 풀린다. 네트워크 단계 앞에서 잡아, 거부되는
    # 쪽이 GitHub에서 수백 파일을 받는 일도 하지 않게 한다. dry_run은 DB를 쓰지 않으므로 잠그지 않는다.
    if not dry_run:
        await _acquire_ingestion_lock(db)

    # 네트워크 단계: 커밋 → 경로 목록 → 원문 받기(클라이언트 설정은 github_client 주석). listed는 트리에 있는
    # 전체 경로(삭제 판정용)이고, limit은 그 뒤에 적용한다. 클라이언트는 Starlette 스레드 풀에서 만든다.
    # httpx가 기본 SSL 컨텍스트를 만들며 certifi CA 번들을 동기로 읽어 Windows 호스트에서 0.3~0.4초가 걸리기
    # 때문이다(2026-10-29, CPU 부하 약 65%에서 4번 재어 0.32~0.43초). 루프 위에서 만들면 그동안 다른 요청이
    # 멈춘다(청킹을 스레드로 보내는 것과 같은 이유). 생성자는 이벤트 루프에 묶이는 것을 만들지 않으므로(연결
    # 풀의 잠금은 처음 쓸 때 만든다) 다른 스레드에서 만들어 이 루프에서 써도 된다. Ollama
    # 호출(app/services/generation.py의 ollama_ssl_context)처럼 컨텍스트를 캐시하지 않는 이유: 적재 한 번에
    # 클라이언트도 한 번이라, 스레드에서 한 번 읽는 쪽이 전역 상태 없이 간단하다.
    client = await run_in_threadpool(github_client)
    async with client:
        sha = await resolve_commit_sha(client, commit_sha)
        paths = await list_doc_paths(client, sha, languages)
        listed = {path for path, _ in paths}
        # 페이지가 하나라도 나온 언어만 사라진 문서를 지운다. 목록이 비었다면 페이지가 정말 하나도 없다기보다
        # 상류의 폴더 구조가 바뀌었거나 언어 이름을 잘못 썼을 가능성이 크기 때문이다.
        listed_languages = sorted({language for _, language in paths})
        if limit is not None:
            paths = paths[:limit]

        # 모든 파일을 gather로 동시에 요청하되, 세마포어로 한 번에 8개까지만 실제로 내려받게 한다.
        semaphore = asyncio.Semaphore(MAX_CONCURRENT_FETCHES)

        async def fetch(path: str, language: str) -> tuple[str, str, str]:
            async with semaphore:
                return path, language, await fetch_raw_file(client, sha, path)

        results = await asyncio.gather(*(fetch(p, lang) for p, lang in paths))

    # DB 단계: 문서를 하나씩 처리한다. 모든 변경은 한 세션 트랜잭션에 쌓였다가 맨 끝에 한 번 커밋된다.
    for path, language, raw_text in results:
        embedder = embedder_for(language)
        # 청커 버전과 임베딩 모델도 해시 키에 넣는다. 그러지 않으면 둘 중 하나를 바꿔도 원문이 같은 문서는
        # 모두 '건너뜀'이 되어, 예전 청크나 다른 모델이 만든 벡터를 조용히 그대로 두게 된다. 모델 식별자에는
        # 고정한 리비전과 자르기 차원도 들어간다(e5와 bge는 모델 이름뿐이다).
        content_hash = hashlib.sha256(
            f"chunker-v{CHUNKER_VERSION}\nembedding-{embedder.identity}\n{raw_text}".encode()
        ).hexdigest()

        # 경로로 기존 문서를 찾고, 해시가 같으면 청킹·임베딩 없이 건너뛴다(재적재가 빠른 이유).
        existing = await db.scalar(select(Document).where(Document.source_path == path))

        if existing is not None and existing.content_hash == content_hash:
            chunks_skipped += 1
            continue

        title = extract_title(raw_text, fallback=path)
        # 청킹(줄마다 tiktoken 인코딩과 정규식)은 문서 하나에 보통 수 ms지만, 가장 큰
        # 문서(en/docs/release-notes.md, 약 695,000자)는 0.3~0.4초가 걸려 루프 위에서 돌면 그동안 다른 요청이
        # 멈춘다(2026-10-29 전 동작). Starlette 기본 스레드 풀(run_in_threadpool)로 보낸다. 모델 스레드
        # 풀(run_model)과 따로 두어 임베딩 뒤에 줄 서지 않게 한다. 청크 내용은 어디서 돌든 같다.
        chunk_results = await run_in_threadpool(chunk_markdown, raw_text)

        # dry_run이면 청크 수만 세고 DB는 건드리지 않는다.
        if dry_run:
            documents_processed += 1
            if existing is not None:
                chunks_updated += len(chunk_results)
            else:
                chunks_created += len(chunk_results)
            continue

        # 바뀐 문서: 기존 청크를 모두 지우고 문서 행의 해시·제목·커밋·처리 시각을 갱신한다(청크는 부분 수정
        # 없이 통째로 교체). 새 문서: 행을 만들고 flush로 DB가 만든 id를 받아 청크의 외래 키에 쓴다.
        if existing is not None:
            await db.execute(delete(Chunk).where(Chunk.document_id == existing.id))
            existing.content_hash = content_hash
            existing.title = title
            existing.source_commit_sha = sha
            existing.fetched_at = func.now()
            document = existing
            chunks_updated += len(chunk_results)
        else:
            document = Document(
                source_path=path,
                title=title,
                source_commit_sha=sha,
                content_hash=content_hash,
            )
            db.add(document)
            await db.flush()
            chunks_created += len(chunk_results)

        # 청크마다 '헤딩 경로 + 본문'(build_embedding_text)을 문서용 접두사로 한 번에 임베딩한다. 검색 때
        # cross-encoder도 같은 입력 형식을 쓴다.
        if chunk_results:
            embedding_texts = [
                build_embedding_text(c.heading_path, c.content) for c in chunk_results
            ]
            # 전체 적재면 몇 분 걸리는 CPU 작업이다. 관리자 API는 이것을 API 프로세스 안에서 돌리므로, 모델
            # 스레드로 보내 그동안에도 서버가 다른 요청에 응답하게 한다.
            embeddings = await run_model(embedder.embed_passages, embedding_texts)

            # 청크와 벡터 개수가 다르면 strict=True가 바로 오류를 내 엉뚱한 짝이 저장되지 않게 한다.
            # chunk_index는 문서 안 순서(0부터), language는 문서 언어다.
            paired = zip(chunk_results, embeddings, strict=True)
            for idx, (chunk_result, embedding) in enumerate(paired):
                db.add(
                    Chunk(
                        document_id=document.id,
                        chunk_index=idx,
                        heading_path=chunk_result.heading_path,
                        content=chunk_result.content,
                        token_count=chunk_result.token_count,
                        embedding=embedding,
                        language=language,
                    )
                )

        documents_processed += 1

    # 트리에서 빠진(또는 새로 제외된) 페이지를 지우지 않으면 계속 검색·인용되어, 더는 없는 페이지로 링크가
    # 걸린다. limit이 있으면 트리의 일부만 처리하므로 이 단계를 하지 않는다. 지운 문서의 청크도 함께 지워진다
    # (ON DELETE CASCADE).
    # 사라진 문서 판정: 이번에 목록에 페이지가 하나라도 있었던 언어의 폴더 아래 문서 중 이번 트리 목록에 없는
    # 것. startswith에 autoescape=True를 줘 경로의 %·_ 같은 문자가 LIKE 와일드카드로 해석되지 않게 한다.
    # ORM 객체를 읽지 않는 일괄 DELETE라 청크 정리는 DB의 ON DELETE CASCADE에 맡기고,
    # synchronize_session=False로 세션 동기화를 생략한다. dry_run이면 지울 개수만 센다.
    if limit is None and listed_languages:
        stale = and_(
            or_(
                *(
                    Document.source_path.startswith(docs_prefix(language), autoescape=True)
                    for language in listed_languages
                )
            ),
            Document.source_path.not_in(listed),
        )
        if dry_run:
            documents_deleted = await db.scalar(
                select(func.count()).select_from(Document).where(stale)
            )
        else:
            result = await db.execute(
                delete(Document).where(stale).execution_options(synchronize_session=False)
            )
            documents_deleted = result.rowcount

    # 모든 변경을 한 번에 커밋한다(적재 잠금도 이때 풀린다). 무언가 바뀌었을 때만 VACUUM을 돌린다(VACUUM은
    # 트랜잭션 밖이어야 하므로 커밋 뒤).
    if not dry_run:
        await db.commit()
        if documents_processed or documents_deleted:
            await _vacuum_chunks(db)

    elapsed_ms = int((time.perf_counter() - start) * 1000)
    return IngestOutcome(
        documents_processed=documents_processed,
        documents_deleted=documents_deleted,
        chunks_created=chunks_created,
        chunks_updated=chunks_updated,
        chunks_skipped=chunks_skipped,
        elapsed_ms=elapsed_ms,
        commit_sha=sha,
    )

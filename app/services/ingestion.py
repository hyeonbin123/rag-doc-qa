"""GitHub에서 FastAPI 문서를 받아 청킹·임베딩하고 Postgres에 넣거나 갱신(upsert)한다.

내용 해시로 멱등하다: 바뀌지 않은 파일은 건너뛰고, 바뀐 파일은 청크를 통째로 교체한다. 그래서 문서가
갱신된 뒤 적재를 다시 돌려도 실제로 바뀐 것만 다시 계산한다. 전체 적재(limit 없음)는 적재한 언어의 문서
중 트리 목록에 더는 없는 것, 즉 상류에서 지워지거나 이름이 바뀌었거나 새로 제외된 페이지도 지운다. 그러면
코퍼스가 그 커밋 시점의 문서와 똑같아진다.
"""

# [파일 역할] FastAPI 공식 문서(GitHub tiangolo/fastapi의 docs/en/docs/, docs/ko/docs/)를 받아 청킹·임베딩하고
# documents·chunks 테이블에 넣는 적재 파이프라인.
# [흐름] 커밋 정하기 → GitHub 트리에서 언어별 마크다운 경로 목록 → 원문을 최대 8개씩 동시에 받기 → 문서마다
# 해시 비교(같으면 건너뜀) → 바뀐 문서는 기존 청크를 지우고 청킹·임베딩해 다시 넣기 → 전체 적재면 트리에서
# 사라진 문서 지우기 → 커밋 → 바뀐 것이 있으면 VACUUM (ANALYZE).
# [설계 이유]
# - 위 docstring처럼 내용 해시로 멱등하게 만들어, 다시 돌려도 바뀐 문서만 처리한다. 해시에 청커 버전과 임베딩
#   모델 식별자를 넣은 이유는 아래 주석과 docs/experiments.md v1→v3, v8에 있다.
# - 임베딩은 몇 분 걸리는 CPU 작업이라 모델 스레드(run_model)에서 돌려 API 서버가 적재 중에도 응답한다.
# [연결] 관리자 API(app/routers/documents.py)와 CLI(scripts/ingest_fastapi_docs.py)가 run_ingestion을,
# scripts/fetch_docs.py가 경로 조회 함수들을 쓴다.

from __future__ import annotations

import asyncio
import hashlib
import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass

# httpx: GitHub API와 raw 파일을 비동기로 받는다. SQLAlchemy: 문서 조회·청크 삭제·사라진 문서 삭제 질의. 앱
# 내부: 모델, 청커, 임베딩 서비스 타입, 모델 스레드, 지원 언어.
import httpx
from sqlalchemy import and_, delete, func, or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chunk import Chunk
from app.models.document import Document
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


# 적재할 커밋을 정한다. 지정했으면 그대로 쓰고, 없으면 master 브랜치의 최신 커밋 SHA를 조회한다. 이후 모든
# 파일을 이 한 커밋에서 받으므로, 적재 도중 상류가 바뀌어도 문서들이 서로 다른 시점으로 섞이지 않는다.
async def resolve_commit_sha(client: httpx.AsyncClient, commit_sha: str | None = None) -> str:
    if commit_sha:
        return commit_sha
    resp = await client.get(f"{GITHUB_API}/repos/{REPO}/commits/master")
    resp.raise_for_status()
    return resp.json()["sha"]


# 커밋의 전체 파일 트리를 한 번에(recursive) 받아 문서 경로를 고른다.
async def list_doc_paths(
    client: httpx.AsyncClient, sha: str, languages: Sequence[str]
) -> list[tuple[str, str]]:
    resp = await client.get(f"{GITHUB_API}/repos/{REPO}/git/trees/{sha}", params={"recursive": "1"})
    resp.raise_for_status()
    data = resp.json()
    # 전체 적재는 목록에 없는 문서를 지우므로, 잘린(일부만 담긴) 목록으로 적재하면 아직 있는 페이지까지
    # 지운다. 그래서 GitHub가 트리 목록을 잘랐다고 알리면 적재를 거부한다.
    if data.get("truncated"):
        raise RuntimeError("GitHub tree listing is truncated; refusing to ingest a partial corpus")
    return select_doc_paths(data["tree"], languages)


# raw.githubusercontent.com에서 커밋 고정 경로로 원문 마크다운 한 파일을 받는다. 실패하면 HTTP 오류 예외가
# 그대로 올라간다.
async def fetch_raw_file(client: httpx.AsyncClient, sha: str, path: str) -> str:
    resp = await client.get(f"{RAW_BASE}/{REPO}/{sha}/{path}")
    resp.raise_for_status()
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
    """
    async with db.bind.connect() as conn:
        conn = await conn.execution_options(isolation_level="AUTOCOMMIT")
        await conn.execute(text("VACUUM (ANALYZE) chunks"))


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
# - limit: 앞에서 n개 경로만 처리(시험용). 이때는 사라진 문서 삭제를 하지 않는다.
# - dry_run: DB를 바꾸지 않고 처리·삭제될 개수만 센다.
# - languages: 적재할 언어(CLI의 --languages). 삭제도 이 언어 범위 안에서만 한다.
async def run_ingestion(
    db: AsyncSession,
    embedder_for: Callable[[str], EmbeddingService],
    commit_sha: str | None = None,
    limit: int | None = None,
    dry_run: bool = False,
    languages: Sequence[str] = DOC_LANGUAGES,
) -> IngestOutcome:
    start = time.perf_counter()
    documents_processed = 0
    documents_deleted = 0
    chunks_created = 0
    chunks_updated = 0
    chunks_skipped = 0

    # 네트워크 단계: 커밋 → 경로 목록 → 원문 받기. User-Agent를 붙이는 것은 GitHub API가 요청에 User-Agent를
    # 요구하기 때문이다. listed는 트리에 있는 전체 경로(삭제 판정용)이고, limit은 그 뒤에 적용한다.
    async with httpx.AsyncClient(
        timeout=30.0, headers={"User-Agent": "rag-doc-qa-ingest"}, follow_redirects=True
    ) as client:
        sha = await resolve_commit_sha(client, commit_sha)
        paths = await list_doc_paths(client, sha, languages)
        listed = {path for path, _ in paths}
        # 페이지가 하나라도 나온 언어만 사라진 문서를 지운다. 목록이 비었다면 페이지가 정말 하나도 없다기보다
        # 상류의 폴더 구조가 바뀌었거나 언어 이름을 잘못 썼을 가능성이 크기 때문이다.
        listed_languages = sorted({language for _, language in paths})
        if limit:
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
        chunk_results = chunk_markdown(raw_text)

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
    if not limit and listed_languages:
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

    # 모든 변경을 한 번에 커밋한다. 무언가 바뀌었을 때만 VACUUM을 돌린다(VACUUM은 트랜잭션 밖이어야 하므로
    # 커밋 뒤).
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

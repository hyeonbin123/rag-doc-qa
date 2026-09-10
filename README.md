# rag-doc-qa

FastAPI 공식 문서를 대상으로 한 RAG(검색 증강 생성) 기반 문서 QA API 서버.

## 아키텍처

```
사용자 질문
   │
   ▼
[JWT 인증] ──▶ [로컬 임베딩(BGE-small)] ──▶ [pgvector 코사인 검색] ──▶ [LLM 답변 생성 + 인용] ──▶ [query_logs 기록]
```

- **백엔드**: FastAPI (Python 3.11, 비동기)
- **저장소**: PostgreSQL 16 + pgvector — 관계형 데이터와 벡터 인덱스를 하나의 DB로 처리 (별도 벡터DB 없음)
- **임베딩**: `BAAI/bge-small-en-v1.5` (로컬 실행, API 비용 없음)
- **답변 생성**: 프로바이더 교체 가능 (`GENERATION_PROVIDER`)
  - `ollama`(기본): 로컬 Qwen2.5-7B, 비용 0원
  - `anthropic`: Claude API, `tool_choice`로 인용 스키마 강제
- **인증**: JWT(access/refresh)
- **평가**: 검색 품질(Hit@k, MRR) + 답변 품질(키워드 커버리지, LLM 판정 충실도/정확도)

## 설계 근거 (자기소개서/면접용 요약)

- **로컬 임베딩 vs API 임베딩**: 코퍼스가 고정되어 있고 데모를 무한정 반복 실행해야 하므로, 비용과 외부 의존성이 없는 로컬 오픈소스 모델을 선택. 대신 BGE 모델의 쿼리/패시지 비대칭 프리픽스를 정확히 구현해야 검색 품질이 나온다는 트레이드오프가 있음.
- **별도 벡터DB 대신 pgvector**: 코퍼스 규모(문서 155개, 청크 약 900개)에서는 관계형 데이터와 벡터를 한 DB에서 처리하는 것이 운영 복잡도 대비 이득이 큼. HNSW 인덱스는 IVFFlat과 달리 list 수 튜닝이 필요 없어 이 규모에 적합.
- **인용을 스키마로 강제**: 프롬프트로 "인용 형식을 지켜라"고 요청하는 대신 스키마를 강제해 파싱 실패 가능성을 구조적으로 제거. Anthropic은 `tool_choice`, Ollama는 `format`(JSON 스키마 제약 디코딩)으로 같은 보장을 얻음.
- **프로바이더별 호출 구조 차이**: 로컬 7B 모델은 JSON 스키마 제약 디코딩 상태에서 문자열 값 안의 따옴표를 제대로 이스케이프하지 못해, 코드가 포함된 답변이 첫 `"`에서 잘리는 문제가 있었음. 그래서 Ollama 경로만 **답변 생성(자유 텍스트)과 인용 추출(숫자만 담긴 스키마)을 2회 호출로 분리**함. Claude는 tool 입력 이스케이프가 안정적이라 1회 호출을 유지.
- **평가 하네스**: 변경할 때마다 같은 30문항으로 전/후를 측정해 `eval/reports/`에 커밋. 실패한 문항은 무엇이 대신 검색됐는지까지 확인한 뒤 다음 수정 방향을 정함 (아래 측정 결과 참고).

## 측정 결과 (2026-09-11, 30문항 평가셋)

### 검색 품질 개선 과정

| 버전 | 변경 | Hit@3 | Hit@10 | MRR |
|---|---|---|---|---|
| v1 | 기본 청커 | 0.93 | 0.97 | 0.828 |
| v2 | MkDocs 마크업 정제 (헤딩 앵커 ID, 코드 include 지시문, admonition, HTML 태그) | 0.97 | 0.97 | 0.911 |
| v3 | v2 + `<dfn>`/`<abbr>` 정의 텍스트 보존 | 0.97 | 0.97 | **0.933** |

- **진단**: 실패한 문항의 상위 10개 유사도가 0.72~0.76의 좁은 구간에 몰려 있었음. 이 구간에서는 모든 헤딩에 붙은 `{ #anchor-id }`(제목이 임베딩에 두 번 들어감)나 실제 코드 없이 경로만 있는 include 지시문 같은 마크업 노이즈가 순위를 좌우함.
- **v2**: 마크업 정제로 MRR 0.828 → 0.911. 백그라운드 작업 질문(q006)이 6위에서 1위로 올라감. 대신 q011은 1위에서 3위로 **회귀**.
- **v3**: 회귀 원인은 정제 로직이 `<dfn title='..."cleanup code"...'>`의 title 속성까지 지운 것이었음. 질문에 나온 "cleanup code"가 바로 그 안에 있었음. 정의 텍스트를 "용어 (정의)" 형태로 보존해 q011을 복구했고 MRR은 0.933.
- 청커를 바꾸면 수집 해시가 달라지도록 `CHUNKER_VERSION`을 해시에 포함함. 원문 해시만 쓰면 청커를 바꿔도 재수집 때 모든 문서가 "변경 없음"으로 스킵되어, 예전 청크로 측정하게 되기 때문.

### 답변 품질 (v3, top_k=5)

| 지표 | 값 |
|---|---|
| 키워드 커버리지 | 0.93 |
| 충실도 (1-5, LLM 판정) | 4.17 |
| 정확도 (1-5, LLM 판정) | 4.73 |
| 판정 모델이 환각으로 표시 | 1 / 30 (아래 한계 참고: 해당 건은 올바른 거절 응답) |
| 평균 응답 시간 | 약 4.6초 (임베딩 44ms + 검색 30ms + 생성 4.5s) |

생성·판정 모델: 로컬 Qwen2.5-7B-Instruct (RTX 2080 Ti, 약 85 tok/s). 판정 점수는 JSON 스키마의 `minimum`/`maximum`으로 1~5 범위를 강제하고, 범위를 벗어나면 평가를 실패시킴. 범위를 설명에만 적어 뒀을 때 판정 모델이 10점 척도로 넘어가 평균이 9점대로 나온 적이 있음.

### 알려진 한계

- **q017 검색 실패**: "secrets like database credentials" 질문이 설정·환경변수 문서 대신 인증 문서(OAuth2, 비밀번호, JWT)로 끌려감. 마크업 정제로는 풀리지 않는, 소형 dense 임베딩의 의미 혼동이라서 BM25+dense 하이브리드 검색을 다음 과제로 둠. 평가셋을 통과시키려고 질문을 바꾸지 않고 실패 사례로 남겨 둠.
- **LLM 판정의 오탐**: q017에서 모델은 검색 실패 후 "컨텍스트에 정보가 없다"고 올바르게 답했지만, 판정 모델은 이를 환각으로 표시함.
- **키워드 커버리지는 거친 지표**: q030은 판정 정확도가 5점인데 답변에 `APIRouter`라는 이름이 없어서 커버리지는 0. 두 지표를 함께 봐야 함.

## 로컬 실행

### 사전 준비
- Docker Desktop (WSL2 backend)
- 생성 프로바이더 중 하나:
  - **Ollama**(기본, 무료): [ollama.com](https://ollama.com) 설치 후 `ollama pull qwen2.5:7b-instruct`. VRAM 6GB 이상 GPU 권장.
  - **Anthropic**: `ANTHROPIC_API_KEY` 발급 후 `.env`에 `GENERATION_PROVIDER=anthropic` 설정

### 1. 환경 변수
```bash
cp .env.example .env
# .env를 열어 ANTHROPIC_API_KEY 등을 채운다
```

### 2. 전체 스택 실행
```bash
docker compose up --build
```
DB 헬스체크 통과 후 API가 마이그레이션(`alembic upgrade head`)을 자동 적용하고 `http://localhost:8000`에서 뜬다. Swagger UI: `http://localhost:8000/docs`.

`.env`는 호스트에서 실행하는 기준(`localhost`)으로 그대로 두면 된다. compose가 API 컨테이너의 `DATABASE_URL`은 `db` 서비스로, `OLLAMA_BASE_URL`은 `host.docker.internal:11434`(호스트에서 실행 중인 Ollama)로 덮어쓴다. 임베딩 모델은 빌드할 때 이미지에 넣어 두므로 실행 중에는 HuggingFace에 접속하지 않고, torch는 CPU 빌드를 써서 이미지 크기는 약 2.2GB다.

### 3. 문서 수집 (최초 1회)
```bash
docker compose exec api python -m scripts.ingest_fastapi_docs
```
FastAPI 공식 문서(GitHub `tiangolo/fastapi`, `docs/en/docs/**/*.md`)를 가져와 청킹·임베딩 후 DB에 적재한다. 재실행해도 내용이 바뀐 문서만 다시 처리한다(content hash 기반 idempotent). 해시에 청커 버전(`CHUNKER_VERSION`)이 포함되어 있어서, 청킹 로직을 바꾸고 버전을 올리면 전체 문서가 자동으로 다시 처리된다. 컨테이너 안에서는 `uv run` 대신 `python -m`으로 실행한다. `uv run`은 실행할 때마다 dev 의존성까지 설치하려고 하기 때문이다.

### 4. 데모 사용자 생성 및 질문
```bash
docker compose exec api python -m scripts.seed_demo_user demo@example.com password123

curl -X POST localhost:8000/auth/login \
  -d "username=demo@example.com&password=password123"
# 응답의 access_token을 아래에 사용

curl -X POST localhost:8000/query/ask \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"question": "How do I declare a path parameter in FastAPI?"}'
```

## 로컬 개발 (Docker 없이 코드만 보는 경우)

```bash
uv sync
uv run alembic upgrade head   # DATABASE_URL이 로컬 Postgres를 가리켜야 함
uv run uvicorn app.main:app --reload
```

## 테스트

```bash
docker compose up -d db
uv run pytest
```
`tests/conftest.py`가 `ragdb_test` 데이터베이스를 대상으로 스키마를 생성/정리한다. 임베딩·생성 서비스는 외부 API 호출 없이 결정론적 fake로 대체된다.

## 평가

```bash
uv run python -m eval.run_retrieval_eval --tag v1_baseline
uv run python -m eval.run_answer_eval --tag v1_baseline
# 판정 LLM 호출 없이 빠르게 반복하려면
uv run python -m eval.run_answer_eval --skip-judge --tag quick
# (청커를 바꿨다면 CHUNKER_VERSION을 올리고 재수집한 뒤)
uv run python -m eval.run_retrieval_eval --tag v2_tuned
```
결과는 `eval/reports/`에 마크다운으로 남는다. 판정 LLM은 `GENERATION_PROVIDER` 설정을 그대로 따르므로, Ollama 설정이면 평가 전체가 무료로 돌아간다.

## 하지 않은 것 (의도적 스코프 제한)

커스텀 프론트엔드, 멀티테넌트 RBAC, 수평 확장, 백그라운드 잡 큐, 스트리밍 응답, 임의 코퍼스 업로드, 임베딩 파인튜닝, 레이트리밋/캐싱 레이어, 이메일 인증/소셜 로그인. 이유는 각 항목이 "포트폴리오 프로젝트의 핵심 역량 증명"과 무관하거나 3~6주 스코프를 벗어나기 때문.

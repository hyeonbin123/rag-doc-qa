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
- **별도 벡터DB 대신 pgvector**: 코퍼스 규모(문서 155개, 청크 971개)에서는 관계형 데이터와 벡터를 한 DB에서 처리하는 것이 운영 복잡도 대비 이득이 큼. HNSW 인덱스는 IVFFlat과 달리 list 수 튜닝이 필요 없어 이 규모에 적합.
- **인용을 스키마로 강제**: 프롬프트로 "인용 형식을 지켜라"고 요청하는 대신 스키마를 강제해 파싱 실패 가능성을 구조적으로 제거. Anthropic은 `tool_choice`, Ollama는 `format`(JSON 스키마 제약 디코딩)으로 같은 보장을 얻음.
- **프로바이더별 호출 구조 차이**: 로컬 7B 모델은 JSON 스키마 제약 디코딩 상태에서 문자열 값 안의 따옴표를 제대로 이스케이프하지 못해, 코드가 포함된 답변이 첫 `"`에서 잘리는 문제가 있었음. 그래서 Ollama 경로만 **답변 생성(자유 텍스트)과 인용 추출(숫자만 담긴 스키마)을 2회 호출로 분리**함. Claude는 tool 입력 이스케이프가 안정적이라 1회 호출을 유지.
- **평가 하네스**: 검색 파라미터(청크 크기, top_k)를 바꾸기 전/후로 측정값을 남겨 "측정하고 개선했다"는 근거를 `eval/reports/`에 커밋.

## 측정 결과 (2026-09-11 기준, 5문항 스타터셋)

| 지표 | 값 |
|---|---|
| Hit@3 / Hit@5 / Hit@10 | 1.00 / 1.00 / 1.00 |
| MRR | 0.800 |
| 답변 충실도 (1-5) | 4.20 |
| 답변 정확도 (1-5) | 4.60 |
| 환각 발생 | 0 / 5 |
| 평균 응답 시간 | 약 4.6초 (임베딩 44ms + 검색 30ms + 생성 4.5s) |

생성 모델: 로컬 Qwen2.5-7B-Instruct (RTX 2080 Ti, 약 85 tok/s)

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

### 3. 문서 수집 (최초 1회)
```bash
docker compose exec api uv run python -m scripts.ingest_fastapi_docs
```
FastAPI 공식 문서(GitHub `tiangolo/fastapi`, `docs/en/docs/**/*.md`)를 가져와 청킹·임베딩 후 DB에 적재한다. 재실행해도 내용이 바뀐 문서만 다시 처리한다(content hash 기반 idempotent).

### 4. 데모 사용자 생성 및 질문
```bash
docker compose exec api uv run python -m scripts.seed_demo_user demo@example.com password123

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
# (청크 크기/오버랩 또는 top_k를 바꾼 뒤)
uv run python -m eval.run_retrieval_eval --tag v2_tuned
```
결과는 `eval/reports/`에 마크다운으로 남는다. 판정 LLM은 `GENERATION_PROVIDER` 설정을 그대로 따르므로, Ollama 설정이면 평가 전체가 무료로 돌아간다.

## 하지 않은 것 (의도적 스코프 제한)

커스텀 프론트엔드, 멀티테넌트 RBAC, 수평 확장, 백그라운드 잡 큐, 스트리밍 응답, 임의 코퍼스 업로드, 임베딩 파인튜닝, 레이트리밋/캐싱 레이어, 이메일 인증/소셜 로그인. 이유는 각 항목이 "포트폴리오 프로젝트의 핵심 역량 증명"과 무관하거나 3~6주 스코프를 벗어나기 때문.

# rag-doc-qa

[![CI](https://github.com/hyeonbin123/rag-doc-qa/actions/workflows/ci.yml/badge.svg)](https://github.com/hyeonbin123/rag-doc-qa/actions/workflows/ci.yml)

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
- **검색 모드**: `RETRIEVAL_MODE=dense`(기본) 또는 `hybrid`(dense 순위와, Postgres `tsvector`로 SQL에서 계산한 BM25 순위를 가중 RRF로 결합). hybrid는 튜닝용 검증셋에서는 앞섰지만 테스트셋에서 dense보다 낮아 기본값으로 쓰지 않음 (아래 v4, v5 참고)
- **평가**: 검색 품질(Hit@k, MRR) + 답변 품질(키워드 커버리지, LLM 판정 충실도/정확도)

## 설계 근거 (자기소개서/면접용 요약)

- **로컬 임베딩 vs API 임베딩**: 코퍼스가 고정되어 있고 데모를 무한정 반복 실행해야 하므로, 비용과 외부 의존성이 없는 로컬 오픈소스 모델을 선택. 대신 BGE 모델의 쿼리/패시지 비대칭 프리픽스를 정확히 구현해야 검색 품질이 나온다는 트레이드오프가 있음.
- **별도 벡터DB 대신 pgvector**: 코퍼스 규모(문서 155개, 청크 약 900개)에서는 관계형 데이터와 벡터를 한 DB에서 처리하는 것이 운영 복잡도 대비 이득이 큼. HNSW 인덱스는 IVFFlat과 달리 list 수 튜닝이 필요 없어 이 규모에 적합.
- **인용을 스키마로 강제**: 프롬프트로 "인용 형식을 지켜라"고 요청하는 대신 스키마를 강제해 파싱 실패 가능성을 구조적으로 제거. Anthropic은 `tool_choice`, Ollama는 `format`(JSON 스키마 제약 디코딩)으로 같은 보장을 얻음.
- **프로바이더별 호출 구조 차이**: 로컬 7B 모델은 JSON 스키마 제약 디코딩 상태에서 문자열 값 안의 따옴표를 제대로 이스케이프하지 못해, 코드가 포함된 답변이 첫 `"`에서 잘리는 문제가 있었음. 그래서 Ollama 경로만 **답변 생성(자유 텍스트)과 인용 추출(숫자만 담긴 스키마)을 2회 호출로 분리**함. Claude는 tool 입력 이스케이프가 안정적이라 1회 호출을 유지.
- **평가 하네스**: 변경할 때마다 전/후를 측정해 `eval/reports/`에 커밋. 실패한 문항은 무엇이 대신 검색됐는지까지 확인한 뒤 다음 수정 방향을 정함. v5부터는 파라미터를 튜닝 전용 검증셋(32문항)에서만 고르고, 테스트셋(30문항)에는 고른 설정 하나만 돌림. 테스트셋을 보면서 고르면 그 셋에 맞춘 튜닝이 되기 때문 (아래 측정 결과 참고).

## 측정 결과 (2026-09-11, 테스트셋 30문항, v5부터 튜닝용 검증셋 32문항 추가)

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

### 하이브리드 검색 실험 (v4, 기본값으로 채택하지 않음)

q017처럼 dense 임베딩이 의미를 혼동하는 경우를 보완하려고, Postgres 전문 검색(생성 컬럼 `tsvector` + GIN 인덱스) 순위와 dense 순위를 RRF(Reciprocal Rank Fusion, k=60)로 합치는 모드를 추가하고 같은 30문항으로 비교함.

| 모드 | Hit@3 | Hit@10 | MRR |
|---|---|---|---|
| dense (v3와 문항 단위까지 동일) | 0.97 | 0.97 | **0.933** |
| hybrid | 0.97 | **1.00** | 0.898 |

- **얻은 것**: q017이 top-10 밖에서 9위로 들어옴. 어휘 검색만 놓고 보면 settings.md가 **1위**였음.
- **잃은 것**: q001(1위→2위), q009(1위→2위), q003(2위→3위). 두 문항 모두 어휘 검색 상위 5개에 정답 문서가 없었고, q009는 모든 기능을 언급하는 `release-notes.md`가 어휘 검색 1위였음.
- **원인**: Postgres `ts_rank`에는 BM25의 IDF(역문서빈도)가 없어서 흔한 단어와 드문 단어를 같은 무게로 셈. "fastapi"는 청크 915개 중 524개(57%)에, "parameter"는 258개(28%)에 나오기 때문에, 질문 단어를 OR로 묶은 어휘 순위가 잡음이 되고, 가중치가 같은 RRF가 그 잡음 때문에 dense의 1위를 밀어냄.
- **결정**: 처음 정한 기준(평균이 나아질 때만 기본값 변경)에 따라 dense를 유지하고, hybrid는 `RETRIEVAL_MODE=hybrid`로 켤 수 있게 남김. 이 30문항에 맞춰 가중치를 고르면 평가셋에 과적합되므로 튜닝하지 않음. 다음 후보는 IDF가 있는 BM25(예: ParadeDB의 `pg_search` 확장)와, 튜닝 전용으로 쓸 별도 검증 질문셋.
- **구현 메모**: 질문 단어는 OR로 묶음. `plainto_tsquery`는 모든 단어를 AND로 묶어서 문장형 질문으로는 거의 아무것도 걸리지 않음. dense 후보는 40개로 제한함. pgvector HNSW 스캔은 한 번에 `hnsw.ef_search`(기본 40)개까지만 돌려주기 때문.

### BM25 + 검증셋 분리 (v5, 기본값으로 채택하지 않음)

v4에서 hybrid가 진 원인으로 `ts_rank`에 IDF가 없다는 점을 지목했으므로, 어휘 순위를 BM25로 바꾸고, 튜닝에 쓰는 질문과 평가에 쓰는 질문을 나눠 다시 측정함.

- **검증셋 분리**: 튜닝 전용 `eval/qa_dev.jsonl` 32문항을 새로 작성하고, 기존 30문항(`qa_dataset.jsonl`)은 테스트셋으로만 씀. 검증셋은 테스트셋이 정답으로 쓰는 문서를 주 정답으로 삼지 않음(보조 정답으로 settings.md, metadata.md 두 개만 겹침). 정답 경로가 DB에 있는지, 기대 키워드가 정답 문서에 실제로 있는지는 스크립트로 확인함.
- **BM25를 SQL로 구현** (`app/services/retrieval.py`): 확장이나 통계 테이블을 추가하지 않음. 질문 어휘소별 문서 빈도(df)는 GIN 인덱스로 세고, 청크 안 빈도(tf)는 `tsvector`의 위치 개수에서, 길이는 `token_count`에서 가져옴 (k1=1.2, b=0.75 기본값, 튜닝하지 않음). ParadeDB `pg_search`는 DB 이미지를 바꿔야 하는데, 이 규모(청크 915개, 어휘 검색 1회 약 40~50ms)에서는 SQL로 충분하다고 판단함. 드문 단어가 반복된 흔한 단어보다 높게 평가되는지는 단위 테스트로 고정함.
- **절차 (측정 전에 정함)**: RRF에서 BM25 목록의 가중치(dense 목록은 1)만 {0.25, 0.5, 0.75, 1.0} 중 검증셋 MRR로 고르고, 고른 설정 하나만 테스트셋에 한 번 돌림. 기본값은 검증셋과 테스트셋 **모두**에서 dense보다 나을 때만 바꿈.

| 설정 | 검증셋 MRR (32문항) | 테스트셋 MRR (30문항) |
|---|---|---|
| dense | 0.858 | **0.933** |
| hybrid, ts_rank (v4) | **0.953** | 0.898 |
| hybrid, BM25 가중치 0.25 / 0.5 / 1.0 | 0.884 / 0.906 / 0.922 | 돌리지 않음 |
| hybrid, BM25 가중치 0.75 (검증셋에서 선택) | **0.953** | 0.894 |

- **결과**: hybrid는 검증셋에서 dense보다 0.095 높았지만 테스트셋에서는 0.039 낮음. 규칙대로 기본값은 dense를 유지하고, hybrid 모드의 어휘 순위를 BM25(가중치 0.75)로 바꿔 opt-in으로 남김.
- **BM25 자체는 의도대로 동작함**: q017의 BM25 순위에서 settings.md가 1위, environment-variables.md가 2위임 (IDF: secret·credential 3.90, fastapi 0.56). q009는 v4에서 2위였던 header-params.md가 1위로 돌아옴.
- **그런데 q017은 최종 결과에서 top-10 밖으로 밀림**: settings.md는 dense 상위 40개에 한 번도 들지 않아서 RRF 점수가 0.75/61 ≈ 0.012에 그침. 반면 두 목록 모두에 걸린 인증 문서 청크는 1/(60+순위)를 두 번 받음(예: 1/65 + 0.75/70 ≈ 0.026). RRF는 두 목록이 모두 적당히 올린 결과를 한 목록만 1위로 올린 결과보다 높게 치는 구조임. q001은 BM25에서 "hint"(IDF 3.66)가 드문 단어라 python-types.md가 1~3위를 차지했고, 최종 순위는 1위에서 3위로 내려감.
- **해석**: 문항 하나가 1위에서 2위로 내려가면 MRR이 약 0.016 바뀜. 가중치별 곡선이 단조롭지 않고(0.884 → 0.906 → 0.953 → 0.922) 두 셋이 반대 방향을 가리키는 것으로 보아, 30문항 규모로는 dense와 hybrid의 차이를 가려내기 어려움. 두 셋을 합친 62문항 평균은 hybrid(약 0.92)가 dense(약 0.89)보다 높지만, 결과를 본 뒤 규칙을 바꾸면 검증셋을 따로 만든 의미가 없어지므로 기본값은 그대로 둠. 두 셋 모두 문서를 읽으면서 작성해서 질문과 본문의 단어가 겹치기 쉽고, 이 편향은 어휘 검색 쪽에 유리하게 작용할 수 있음.
- **다음 후보**: 두 목록의 후보를 합친 뒤 cross-encoder로 재정렬(reranker)하면, 한 목록에만 있는 정답(q017)을 순위 합산 없이 질문과 직접 비교해 판단할 수 있음. 결론을 내리려면 새 질문으로 테스트셋 자체도 키워야 함.

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

- **q017 검색 실패**: "secrets like database credentials" 질문이 설정·환경변수 문서 대신 인증 문서(OAuth2, 비밀번호, JWT)로 끌려감. 마크업 정제로는 풀리지 않는, 소형 dense 임베딩의 의미 혼동이고, settings.md는 dense 상위 40개에 들지 않음. BM25 순위만 보면 settings.md가 1위지만, RRF로 합치면 두 목록에 모두 걸린 인증 문서에 밀려 hybrid에서도 top-10 밖임 (위 v5 참고). 평가셋을 통과시키려고 질문을 바꾸지 않고 실패 사례로 남겨 둠.
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
`tests/conftest.py`는 `ragdb_test` 데이터베이스와 스키마에 필요한 확장(`vector`, `pgcrypto`)이 없으면 직접 만들고, 테스트마다 스키마를 생성·정리한다. 임베딩·생성 서비스는 외부 API를 부르지 않는 결정론적 fake로 대체된다. push와 PR마다 GitHub Actions가 pgvector 서비스 컨테이너를 띄워 같은 ruff + pytest를 실행한다 (`.github/workflows/ci.yml`).

## 평가

```bash
uv run python -m eval.run_retrieval_eval --tag v1_baseline
uv run python -m eval.run_answer_eval --tag v1_baseline
# 판정 LLM 호출 없이 빠르게 반복하려면
uv run python -m eval.run_answer_eval --skip-judge --tag quick
# (청커를 바꿨다면 CHUNKER_VERSION을 올리고 재수집한 뒤)
uv run python -m eval.run_retrieval_eval --tag v2_tuned
# dense와 hybrid 비교 (--mode를 생략하면 RETRIEVAL_MODE 설정을 따름)
uv run python -m eval.run_retrieval_eval --mode dense --tag v4_dense
uv run python -m eval.run_retrieval_eval --mode hybrid --tag v4_hybrid
# 파라미터 튜닝은 검증셋으로만 한다 (--dataset 기본값은 테스트셋인 eval/qa_dataset.jsonl)
uv run python -m eval.run_retrieval_eval --mode hybrid --dataset eval/qa_dev.jsonl --lexical-weight 0.5 --tag dev_w050
```
결과는 `eval/reports/`에 마크다운으로 남는다. 판정 LLM은 `GENERATION_PROVIDER` 설정을 그대로 따르므로, Ollama 설정이면 평가 전체가 무료로 돌아간다.

## 하지 않은 것 (의도적 스코프 제한)

커스텀 프론트엔드, 멀티테넌트 RBAC, 수평 확장, 백그라운드 잡 큐, 스트리밍 응답, 임의 코퍼스 업로드, 임베딩 파인튜닝, 레이트리밋/캐싱 레이어, 이메일 인증/소셜 로그인. 이유는 각 항목이 "포트폴리오 프로젝트의 핵심 역량 증명"과 무관하거나 3~6주 스코프를 벗어나기 때문.

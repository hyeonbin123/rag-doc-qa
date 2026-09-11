# HANDOFF

## Goal
자기소개서용 포트폴리오 프로젝트(RAG 문서 QA API). 진행한 단계:
- 2단계: 평가셋 확장과 검색 개선
- 3단계: Docker 전체 스택 검증
- 4단계: 하이브리드 검색(dense + Postgres 전문 검색, RRF) 실험. 측정해 보니 평균이 더 나빠서 기본값은 dense로 유지
- 5단계: GitHub Actions CI(ruff + pytest) 추가
- 6단계: 어휘 순위를 BM25로 바꾸고 튜닝 전용 검증셋을 분리해 다시 측정. 미리 정한 규칙(검증셋과 테스트셋 모두에서 dense보다 나아야 함)을 통과하지 못해 기본값은 여전히 dense
- 7단계: cross-encoder 재정렬(`RETRIEVAL_MODE=rerank`) 추가. q017을 1위로 끌어올리고 답변 품질도 좋아졌지만, 미리 정한 기준인 테스트셋 MRR에서 dense보다 낮아 기본값은 dense 유지

## Done
- FastAPI 앱(auth/documents/query/logs/health), SQLAlchemy 모델 4종, Alembic 마이그레이션(pgvector + HNSW), 수집 파이프라인, 평가 하네스
- 생성 프로바이더 추상화: `GENERATION_PROVIDER=ollama`(기본, 로컬 Qwen2.5-7B) / `anthropic`. Ollama 경로는 답변(자유 텍스트)과 인용(숫자 스키마)을 2회 호출로 나눔. 7B 모델이 제약 디코딩 중 문자열 안의 따옴표를 이스케이프하지 못해 코드가 든 답변이 잘렸기 때문
- GitHub 공개 저장소: https://github.com/hyeonbin123/rag-doc-qa
- **평가셋 5 → 30문항** (`eval/qa_dataset.jsonl`): 실제 수집된 코퍼스 내용을 보고 작성했고, 참조하는 `expected_source_paths`가 모두 DB에 있는지 확인함
- **검색 개선 v1 → v2 → v3** (30문항 기준 MRR 0.828 → 0.911 → 0.933)
  - v2: `clean_markdown()` 추가. MkDocs 헤딩 앵커 `{ #id }`, 코드 include 지시문 `{* ... *}`, admonition 구분자, HTML 태그를 제거함 (코드 펜스와 인라인 코드는 그대로 둠)
  - v3: v2가 `<dfn title="...">`의 정의 텍스트까지 지워서 q011이 회귀함 → `<dfn>`/`<abbr>`는 "용어 (정의)" 형태로 보존
- **잠재 버그 수정**: 수집 해시가 원문만 보고 있어서, 청커를 바꿔도 모든 문서가 "변경 없음"으로 스킵됐음 → `CHUNKER_VERSION`을 해시에 포함 (`app/services/ingestion.py`)
- **평가 버그 수정**: 판정 점수 범위가 설명 문구에만 있어서 로컬 판정 모델이 10점 척도로 넘어감(평균 9.17) → 스키마에 `minimum`/`maximum` 추가, 범위를 벗어나면 `ValueError`로 평가를 실패시킴, 리포트에 문항별 표 추가 (`eval/run_answer_eval.py`). 무효 측정이었던 v2 답변 리포트는 삭제함
- **Docker 전체 스택 (3단계)**:
  - `.dockerignore` 추가. 없으면 `COPY . .`가 Windows `.venv`로 컨테이너의 Linux venv를 덮어쓰고, `.env`(API 키)가 이미지에 들어감
  - compose에서 api 컨테이너의 `DATABASE_URL`을 `db`로, `OLLAMA_BASE_URL`을 `host.docker.internal:11434`로 덮어씀. 이 PC에서는 Ollama를 127.0.0.1에 바인딩한 그대로도 컨테이너에서 접근됨(HTTP 200 확인)
  - torch를 PyTorch CPU 인덱스로 고정. `tool.uv.sources`는 전이 의존성에는 적용되지 않아 `torch`를 직접 의존성으로 추가해야 했음 → lock에서 nvidia 패키지 15개와 triton 제거
  - Dockerfile: 모델 다운로드를 소스 복사 앞으로 옮김, `HF_HUB_OFFLINE=1` 추가, 효과가 없던 `--extra-index-url` 제거
  - README의 컨테이너 명령을 `uv run`에서 `python -m`으로 변경 (컨테이너 안에서 `uv run`을 쓰면 dev 의존성을 설치함)
- **하이브리드 검색 실험 (4단계)**:
  - `chunks.content_tsv`: Postgres가 관리하는 생성 컬럼(`to_tsvector('english', heading_path || content)`) + GIN 인덱스 (마이그레이션 0002). DB가 계산하므로 수집 코드는 바꾸지 않음
  - `hybrid_search` / `retrieve()` (`app/services/retrieval.py`), `RETRIEVAL_MODE` 설정(기본 `dense`), API와 두 평가 스크립트의 `--mode` 옵션
  - 30문항 결과: dense MRR 0.933 vs hybrid 0.898. 원인으로 본 것: `ts_rank`에 IDF가 없어서 "fastapi"(청크의 57%) 같은 흔한 단어가 어휘 순위를 흐림
- **CI (5단계)**: `.github/workflows/ci.yml`. push와 PR마다 pgvector 서비스 컨테이너를 띄우고 `uv sync --frozen` → ruff → pytest (Python 3.11, `astral-sh/setup-uv@v10.1.0`, `actions/checkout@v7`. setup-uv는 `v10` 같은 주 버전 태그를 만들지 않으므로 정확한 릴리스 태그로 고정해야 함). 서비스 컨테이너는 일부러 `ragdb`만 만들어서, 새로 클론한 환경처럼 테스트 DB가 없는 상태를 매번 검증하게 함
  - `tests/conftest.py`가 `ragdb_test` 데이터베이스와 `vector`/`pgcrypto` 확장이 없으면 직접 만들도록 수정
- **BM25 + 검증셋 분리 (6단계)**:
  - `eval/qa_dev.jsonl` 32문항 신규 작성 (튜닝 전용). 테스트셋이 정답으로 쓰는 문서를 주 정답으로 삼지 않음. 경로와 키워드는 `work/check_dev_set.py`로 DB와 대조함 (work/는 gitignore)
  - `hybrid_search`의 어휘 순위를 `ts_rank`에서 SQL로 계산하는 BM25로 교체. df는 GIN 인덱스로, tf는 tsvector 위치 개수로, 길이는 `token_count`로 계산 (k1=1.2, b=0.75). 스키마 변경 없음. `lexical_search()`로 BM25 순위만 따로 볼 수 있음
  - RRF 가중치 `LEXICAL_WEIGHT = 0.75` (검증셋에서 {0.25, 0.5, 0.75, 1.0} 중 선택)
  - 결과: 검증셋 MRR dense 0.858 / BM25 hybrid 0.953, 테스트셋 dense 0.933 / BM25 hybrid 0.894 → 기본값 dense 유지
- **Cross-encoder 재정렬 (7단계)**:
  - `app/services/reranking.py`: `RerankerService`(sentence-transformers `CrossEncoder`, 점수는 sigmoid로 0~1). `get_reranker_service()`는 `RERANKER_MODEL_NAME`(기본 `cross-encoder/ms-marco-MiniLM-L-6-v2`)을 씀
  - `rerank_search()` (`app/services/retrieval.py`): dense 상위 N개와 BM25 상위 N개의 합집합을 재정렬. 모델 호출은 `asyncio.to_thread`로 실행. `RERANK_POOL = 5` (검증셋에서 {5, 10, 20} 중 지연 예산 1초 안에서 선택)
  - `RETRIEVAL_MODE=rerank`일 때만 모델을 불러옴 (`get_reranker` 의존성, lifespan에서 미리 로드). API의 retrieval 지연에 재정렬 시간이 포함됨
  - 평가: `run_retrieval_eval.py`에 `--mode rerank`, `--rerank-pool`, `--reranker-model`, 검색 지연 p50/p95 기록 추가. `run_answer_eval.py`에 `--mode rerank` 추가
  - Dockerfile에서 재정렬 모델도 이미지에 넣음 (이미지 2.35GB). 컨테이너에서 오프라인(`HF_HUB_OFFLINE=1`)으로 로드되는 것 확인
  - 결과: 테스트셋 MRR dense 0.933 / rerank 0.889 (Hit@3 0.97 → 1.00), 답변 품질은 rerank가 나음 (커버리지 1.00, 충실도 4.27, 정확도 4.87, 환각 0/30 vs dense 0.93 / 4.17 / 4.73 / 1/30). 자세한 분석은 README v6 절

## Files touched
- 2단계: `app/services/chunking.py`, `app/services/ingestion.py`, `eval/qa_dataset.jsonl`, `eval/run_answer_eval.py`, `eval/reports/*`, `tests/test_chunking.py`, `README.md`
- 3단계: `.dockerignore`, `Dockerfile`, `docker-compose.yml`, `pyproject.toml`, `uv.lock`, `README.md`
- 4단계: `alembic/versions/0002_chunks_fulltext.py`, `app/models/chunk.py`, `app/services/retrieval.py`, `app/config.py`, `app/routers/query.py`, `eval/run_retrieval_eval.py`, `eval/run_answer_eval.py`, `tests/test_retrieval.py`, `.env.example`, `README.md`, `eval/reports/retrieval_eval_v4_*`
- 5단계: `.github/workflows/ci.yml`, `tests/conftest.py`, `README.md`
- 6단계: `app/services/retrieval.py`, `eval/qa_dev.jsonl`, `eval/run_retrieval_eval.py`, `tests/test_retrieval.py`, `.env.example`, `README.md`, `eval/reports/retrieval_eval_v5_*`
- 7단계: `app/services/reranking.py`(신규), `app/services/retrieval.py`, `app/config.py`, `app/dependencies.py`, `app/main.py`, `app/routers/query.py`, `eval/run_retrieval_eval.py`, `eval/run_answer_eval.py`, `tests/test_retrieval.py`, `Dockerfile`, `.env.example`, `README.md`, `eval/reports/*_v6_*`

## Test results
- `ruff check .` 통과, `pytest` 29개 통과 (7단계에서 재정렬 테스트 3개 추가: dense·BM25 후보 합집합을 재정렬 점수 순으로 돌려주는지, top_k를 지키는지, 재정렬 모델 없이 rerank 모드를 부르면 오류가 나는지)
- 새 클론 조건 재현(5단계): `ragdb_test`를 삭제한 상태에서 pytest 통과. 원격 CI 결과는 README 배지 또는 GitHub Actions 탭에서 확인
- `docker compose build api` 성공, 컨테이너에서 재정렬 모델 오프라인 로드 확인 (7단계)
- 7단계 리포트 (`eval/reports/`):
  - 검증셋: `retrieval_eval_v6_dev_dense_*` (MRR 0.858, p50 10ms), `v6_dev_rerank_p05/p10/p20_*` (0.969 / 0.953 / 0.945, p50 627 / 1383 / 2700ms)
  - 테스트셋: `retrieval_eval_v6_test_dense_*` (MRR 0.933), `v6_test_rerank_p05_*` (Hit@3 1.00, Hit@10 1.00, MRR 0.889, p50 620ms)
  - 답변 품질(테스트셋): `answer_eval_v6_dense_rerun_*` (v3와 집계 동일), `answer_eval_v6_rerank_p05_*`
- 6단계 리포트: 검증셋 `retrieval_eval_v5_dev_*`, 테스트셋 `retrieval_eval_v5_test_bm25_w075_*` (MRR 0.894)
- 클린 클론(`git clone` 후 `.env.example`만 복사): README 절차 그대로 빌드 → 빈 DB에 수집 155문서/915청크 → 데모 사용자 생성 → 로그인 → 인용이 붙은 답변 (3단계에서 확인. 7단계 이후 클린 클론 전체 재검증은 하지 않음, 이미지 빌드와 모델 로드만 확인)

## 환경 메모
- DB 컨테이너는 Docker Desktop이 재시작되면 내려갈 수 있음 → `docker compose up -d db`로 다시 올리면 됨. 데이터는 `pgdata` 볼륨에 남아 있음
- **Docker는 `coding\start-docker.cmd`로 시작** (로그인할 때는 작업 스케줄러의 "Start Docker Desktop (coding)"이 같은 스크립트를 자동으로 실행함). 이 PC의 Docker Desktop 4.90은 종료할 때마다(정상 종료 포함) 지울 수 없는 AF_UNIX 소켓 파일(Error 1920)을 남기고, 다음 시작 때 이를 치우다 실패하면서 "Quit / Reset to factory defaults" 오류 창을 띄움. 스크립트는 시작 전에 소켓 폴더(`%LOCALAPPDATA%\Docker\run`, `%LOCALAPPDATA%\docker-secrets-engine`)를 `%LOCALAPPDATA%\Docker\stale-sockets\`로 옮김. Claude 도구에서는 Docker Desktop을 직접 실행하지 말고 `Start-ScheduledTask -TaskName "Start Docker Desktop (coding)"`으로 띄울 것 (이렇게 띄운 Docker는 Claude의 Job 바깥에서 실행되는 것을 확인함). **"Reset to factory defaults"는 볼륨(DB)을 지우므로 누르지 말 것**
- 청커를 고치면 `CHUNKER_VERSION`을 올리고 재수집해야 새 청크 기준으로 측정됨
- 검색 파라미터를 바꿀 때는 `--dataset eval/qa_dev.jsonl`로만 비교하고, 테스트셋(`qa_dataset.jsonl`)은 최종 설정 하나에만 돌릴 것
- 지연 시간을 잴 때는 평가를 동시에 여러 개 돌리지 말 것 (CPU를 나눠 써서 재정렬 지연이 부풀려짐)
- torch는 CPU 빌드라 이 PC의 RTX 2080 Ti를 쓰지 않음. 재정렬이 느린 주된 이유

## TODO / 미완료 작업
- **기본값 결정 보류**: 검색 순위(MRR) 기준으로는 dense, RAG 전체 결과(Hit@k, 답변 품질) 기준으로는 rerank가 나음. 기준을 답변 품질로 바꾸려면, 문서를 보지 않고 사용자 입장에서 먼저 쓴 새 테스트셋에서 미리 정한 기준으로 다시 확인할 것 (현재 두 셋은 문서를 보며 작성해서 질문과 본문의 어휘가 겹치기 쉬운 편향이 있음)
- 30문항 규모로는 방법 간 차이를 가려내기 어려움 (문항 하나가 순위 1칸 바뀌면 MRR 약 0.016)
- Anthropic 경로는 코드만 있고 실제로 돌려 본 적 없음 (API 크레딧 없음). 크레딧을 충전하면 `GENERATION_PROVIDER=anthropic`으로 같은 흐름을 다시 검증
- `%LOCALAPPDATA%\Docker\stale-sockets\`에 옮겨 둔 소켓 폴더들은 Docker 동작과 무관함. 안의 파일은 0바이트라 용량 문제는 없고, 일반적인 방법으로는 지워지지 않음

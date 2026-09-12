# HANDOFF

## Goal
자기소개서용 포트폴리오 프로젝트(RAG 문서 QA API). 진행한 단계:
- 2단계: 평가셋 확장과 검색 개선
- 3단계: Docker 전체 스택 검증
- 4단계: 하이브리드 검색(dense + Postgres 전문 검색, RRF) 실험. 측정해 보니 평균이 더 나빠서 기본값은 dense로 유지
- 5단계: GitHub Actions CI(ruff + pytest) 추가
- 6단계: 어휘 순위를 BM25로 바꾸고 튜닝 전용 검증셋을 분리해 다시 측정. 미리 정한 규칙(검증셋과 테스트셋 모두에서 dense보다 나아야 함)을 통과하지 못해 기본값은 여전히 dense
- 7단계: cross-encoder 재정렬(`RETRIEVAL_MODE=rerank`) 추가. q017을 1위로 끌어올리고 답변 품질도 좋아졌지만, 미리 정한 기준인 테스트셋 MRR에서 dense보다 낮아 기본값은 dense 유지
- 8단계: 문서를 보기 전에 쓴 새 테스트셋(43문항)에서 답변 정확도를 기준으로 재판정. 동점(4.60)이라 기본값을 dense로 확정. README를 채용 담당자가 빨리 볼 수 있게 재구성하고 실험 기록은 `docs/experiments.md`로 분리

## Done
- FastAPI 앱(auth/documents/query/logs/health), SQLAlchemy 모델 4종, Alembic 마이그레이션(pgvector + HNSW), 수집 파이프라인, 평가 하네스
- 생성 프로바이더 추상화: `GENERATION_PROVIDER=ollama`(기본, 로컬 Qwen2.5-7B) / `anthropic`. Ollama 경로는 답변(자유 텍스트)과 인용(숫자 스키마)을 2회 호출로 나눔. 7B 모델이 제약 디코딩 중 문자열 안의 따옴표를 이스케이프하지 못해 코드가 든 답변이 잘렸기 때문
- GitHub 공개 저장소: https://github.com/hyeonbin123/rag-doc-qa
- **평가셋 5 → 30문항** (`eval/qa_dataset.jsonl`): 실제 수집된 코퍼스 내용을 보고 작성했고, 참조하는 `expected_source_paths`가 모두 DB에 있는지 확인함
- **검색 개선 v1 → v2 → v3** (30문항 기준 MRR 0.828 → 0.911 → 0.933): `clean_markdown()`으로 MkDocs 마크업 노이즈 제거, `<dfn>`/`<abbr>` 정의 텍스트는 보존
- **잠재 버그 수정**: 수집 해시에 `CHUNKER_VERSION` 포함 (`app/services/ingestion.py`). 원문만 해시하면 청커를 바꿔도 모든 문서가 "변경 없음"으로 스킵됐음
- **평가 버그 수정**: 판정 점수 범위를 JSON 스키마의 `minimum`/`maximum`으로 강제하고 범위를 벗어나면 `ValueError` (`eval/run_answer_eval.py`)
- **Docker 전체 스택 (3단계)**: `.dockerignore`, compose의 `DATABASE_URL`/`OLLAMA_BASE_URL` 덮어쓰기, torch CPU 인덱스 고정(직접 의존성으로 선언해야 `tool.uv.sources`가 적용됨), 모델을 이미지에 미리 넣고 `HF_HUB_OFFLINE=1`
- **하이브리드 검색 (4단계)**: `chunks.content_tsv` 생성 컬럼 + GIN 인덱스 (마이그레이션 0002), `RETRIEVAL_MODE` 설정
- **CI (5단계)**: `.github/workflows/ci.yml`. pgvector 서비스 컨테이너, `uv sync --frozen` → ruff → pytest. `astral-sh/setup-uv@v10.1.0`처럼 정확한 릴리스 태그로 고정해야 함(주 버전 태그 없음). `tests/conftest.py`가 테스트 DB와 확장을 직접 만듦
- **BM25 + 검증셋 분리 (6단계)**: `eval/qa_dev.jsonl` 32문항(튜닝 전용), SQL로 계산하는 BM25(`lexical_search`), RRF 가중치 `LEXICAL_WEIGHT = 0.75`
- **Cross-encoder 재정렬 (7단계)**: `app/services/reranking.py`, `rerank_search()` (dense·BM25 각 상위 5개의 합집합 재정렬, `RERANK_POOL = 5`, `asyncio.to_thread`), `RETRIEVAL_MODE=rerank`일 때만 모델 로드, 평가 스크립트에 검색 지연 p50/p95 기록, Dockerfile에 재정렬 모델 포함(이미지 2.35GB)
- **새 테스트셋 재판정 (8단계)**:
  - `eval/qa_test2.jsonl` 43문항. 사용자 입장에서 질문 44개를 먼저 쓰고(`eval/qa_test2_draft.md`), 정답 문서는 그다음에 DB에서 검색해 찾음(`work/locate_answers.py`). 코퍼스에 설명이 없는 1문항만 제외, 질문 문구는 바꾸지 않음. 경로·키워드는 `work/check_dev_set.py eval/qa_test2.jsonl`로 대조
  - 판단 규칙을 측정 전에 정함: 주 지표는 답변 정확도, 보조 조건은 Hit@5가 dense보다 낮지 않을 것, 동점이면 dense
  - 결과: Hit@5 dense 0.88 / rerank 0.93, 답변 정확도 둘 다 4.60(43문항 합계 198점 동점) → 기본값 dense 확정. 문항별로는 rerank에서 8개가 오르고(+10점) 7개가 내림(−10점). 분석은 `docs/experiments.md` v7 절
  - `eval/run_answer_eval.py`에 `--dataset` 옵션 추가
  - README 재구성: 한눈에 보기 표, mermaid 구조도, 실제 응답 예시, 단계별 핵심 결과, 설계 판단, 알려진 한계. v1~v7 상세 기록은 `docs/experiments.md`로 옮김
  - `docker-compose.yml`의 DB 호스트 포트를 `${POSTGRES_HOST_PORT:-5432}`로 바꿔 설정 가능하게 함 (`.env.example`, README에 설명)

## Files touched
- 2~5단계: `app/services/chunking.py`, `app/services/ingestion.py`, `eval/*`, `tests/*`, `.dockerignore`, `Dockerfile`, `docker-compose.yml`, `pyproject.toml`, `uv.lock`, `alembic/versions/0002_chunks_fulltext.py`, `app/models/chunk.py`, `app/services/retrieval.py`, `app/config.py`, `app/routers/query.py`, `.github/workflows/ci.yml`, `README.md`
- 6단계: `app/services/retrieval.py`, `eval/qa_dev.jsonl`, `eval/run_retrieval_eval.py`, `tests/test_retrieval.py`, `.env.example`, `README.md`, `eval/reports/retrieval_eval_v5_*`
- 7단계: `app/services/reranking.py`(신규), `app/services/retrieval.py`, `app/config.py`, `app/dependencies.py`, `app/main.py`, `app/routers/query.py`, `eval/run_retrieval_eval.py`, `eval/run_answer_eval.py`, `tests/test_retrieval.py`, `Dockerfile`, `.env.example`, `README.md`, `eval/reports/*_v6_*`
- 8단계: `eval/qa_test2.jsonl`(신규), `eval/qa_test2_draft.md`(신규), `docs/experiments.md`(신규), `eval/run_answer_eval.py`, `docker-compose.yml`, `.env.example`, `README.md`, `HANDOFF.md`, `eval/reports/*_v7_*`

## Test results
- `ruff check .` 통과, `pytest` 29개 통과 (8단계에서 DB를 호스트 포트 55432로 띄운 상태로 실행)
- 8단계 리포트 (`eval/reports/`): `retrieval_eval_v7_test2_dense_*`, `retrieval_eval_v7_test2_rerank_p05_*`, `answer_eval_v7_test2_dense_*`, `answer_eval_v7_test2_rerank_*`
- 7단계 리포트: `retrieval_eval_v6_*`, `answer_eval_v6_*` / 6단계: `retrieval_eval_v5_*`
- `docker compose config`: `POSTGRES_HOST_PORT`가 없으면 5432, 지정하면 그 포트로 게시되는 것 확인
- README 응답 예시: 로컬에서 `uvicorn`을 띄우고 README 4단계 방식으로 만든 로컬 데모 계정(`readme-demo@example.com`)으로 로그인해 실제로 받은 응답. 응답 전체는 `query_logs`에도 남아 있음
- 7단계: `docker compose build api` 성공, 컨테이너에서 재정렬 모델 오프라인 로드 확인. 클린 클론 전체 재검증은 3단계가 마지막

## 환경 메모
- **DB 포트**: 2026-09-12 재부팅 뒤 Windows(Hyper-V/WSL)가 TCP 5432~5631을 예약해서 DB가 5432에 바인딩하지 못했음. 이때는 셸에서 `$env:POSTGRES_HOST_PORT='55432'`로 `docker compose up -d db`를 하고, 명령마다 `$env:DATABASE_URL='postgresql+asyncpg://raguser:ragpass@localhost:55432/ragdb'`, `$env:TEST_DATABASE_URL='...:55432/ragdb_test'`를 설정해서 실행함 (`.env`는 수정하지 않음). 예약 범위는 부팅마다 바뀔 수 있으니 `netsh interface ipv4 show excludedportrange protocol=tcp`로 먼저 확인. 5432를 영구히 쓰려면 관리자 권한으로 예약을 풀고 5432를 제외 목록에 넣어야 하는데, 이는 사용자가 결정할 시스템 설정 변경임
- **Docker는 `coding\start-docker.cmd`로 시작** (로그인할 때는 작업 스케줄러의 "Start Docker Desktop (coding)"이 같은 스크립트를 자동 실행하며, 2026-09-12 재부팅에서 정상 동작 확인). 이 PC의 Docker Desktop 4.90은 종료할 때마다 지울 수 없는 AF_UNIX 소켓 파일을 남기고 다음 시작 때 실패하므로, 스크립트가 소켓 폴더를 `%LOCALAPPDATA%\Docker\stale-sockets\`로 옮긴 뒤 시작함. Claude 도구에서는 Docker Desktop을 직접 실행하지 말고 `Start-ScheduledTask -TaskName "Start Docker Desktop (coding)"`을 쓸 것. **"Reset to factory defaults"는 볼륨(DB)을 지우므로 누르지 말 것**
- 청커를 고치면 `CHUNKER_VERSION`을 올리고 재수집해야 새 청크 기준으로 측정됨
- 검색 파라미터는 `--dataset eval/qa_dev.jsonl`로만 비교하고, 테스트셋(`qa_dataset.jsonl`, `qa_test2.jsonl`)은 최종 설정에만 돌릴 것
- 지연 시간을 잴 때는 평가를 동시에 여러 개 돌리지 말 것 (CPU를 나눠 써서 재정렬 지연이 부풀려짐). 답변 평가도 Ollama 요청이 섞이지 않게 하나씩 돌림
- torch는 CPU 빌드라 이 PC의 RTX 2080 Ti를 쓰지 않음. 재정렬이 느린 주된 이유
- 로컬 DB의 `demo@example.com` 계정은 예전에 다른 비밀번호로 만들어져 README 절차의 비밀번호로는 로그인되지 않음

## TODO / 미완료 작업
- **자기소개서 문구 초안** (다음 단계): 백엔드용, 데이터·AI용 두 버전. README "설계 판단"과 "핵심 결과"가 근거 자료
- 답변 정확도를 더 올리려면 검색보다 생성 쪽이 먼저임 (v7 해석): 더 큰 생성 모델, 또는 판정을 여러 번 해서 평균을 내 판정 흔들림 줄이기
- t030처럼 정답 문서를 둘 이상 인정하면서 참고 답안은 하나만 쓴 문항은 판정이 불공정할 수 있음. 새 질문셋을 만들 때는 인정하는 답마다 참고 답안에 반영할 것
- Anthropic 경로는 코드만 있고 실제로 돌려 본 적 없음 (API 크레딧 없음). 크레딧을 충전하면 `GENERATION_PROVIDER=anthropic`으로 같은 흐름을 다시 검증
- `%LOCALAPPDATA%\Docker\stale-sockets\`에 옮겨 둔 소켓 폴더들은 Docker 동작과 무관함. 안의 파일은 0바이트라 용량 문제는 없고, 일반적인 방법으로는 지워지지 않음

# HANDOFF

## Goal
자기소개서용 포트폴리오 프로젝트(RAG 문서 QA API). 평가셋 확장·검색 개선(2단계)과 Docker 전체 스택 검증(3단계)까지 완료했다. 클린 클론에서 README 절차만 따라 처음부터 끝까지 동작하는 것도 확인했다.

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
  - torch를 PyTorch CPU 인덱스로 고정. `tool.uv.sources`는 전이 의존성에는 적용되지 않아 `torch`를 직접 의존성으로 추가해야 했음 → lock에서 nvidia 패키지 15개와 triton 제거, 이미지 2.17GB
  - Dockerfile: 모델 다운로드를 소스 복사 앞으로 옮김, `HF_HUB_OFFLINE=1` 추가, 효과가 없던 `--extra-index-url` 제거
  - README의 컨테이너 명령을 `uv run`에서 `python -m`으로 변경 (컨테이너 안에서 `uv run`을 쓰면 dev 의존성을 설치함)

## Files touched
- 2단계: `app/services/chunking.py`, `app/services/ingestion.py`, `eval/qa_dataset.jsonl`, `eval/run_answer_eval.py`, `eval/reports/*`, `tests/test_chunking.py`, `README.md`
- 3단계: `.dockerignore`, `Dockerfile`, `docker-compose.yml`, `pyproject.toml`, `uv.lock`, `README.md`

## Test results
- `ruff check .` 통과, `pytest` 22개 통과 (CPU torch로 교체한 뒤 실제 임베딩 스모크 테스트도 통과)
- `eval/reports/retrieval_eval_v3_keep_definitions_20260910_221511.md`: Hit@3 0.97, Hit@10 0.97, MRR 0.933
- `eval/reports/answer_eval_v3_keep_definitions_20260910_222402.md`: 키워드 커버리지 0.93, 충실도 4.17, 정확도 4.73, 판정상 환각 1/30 (q017의 올바른 거절 응답을 판정 모델이 잘못 분류한 것)
- 컨테이너 스택: 모델을 로드할 때 HuggingFace 요청 없음(로그 확인). 컨테이너 안에서 수집 dry-run을 돌리면 호스트와 같은 해시로 스킵됨
- **클린 클론**(`git clone` 후 `.env.example`만 복사): README 절차 그대로 빌드 → api healthy(13초) → 빈 DB에 컨테이너 안에서 수집 155문서/915청크(호스트와 동일, 2분 20초) → 데모 사용자 생성 → 로그인 → 질문(q006)에 `background-tasks.md`를 인용한 답변, 총 10.7초

## 환경 메모
- Docker Desktop이 재시작되면 DB 컨테이너가 내려갈 수 있음 → `docker compose up -d db`로 다시 올리면 됨. 데이터는 `pgdata` 볼륨에 남아 있음
- `ragdb_test`에는 `vector`, `pgcrypto` 확장을 직접 만들어 둬야 함 (`docker/postgres/init.sql`은 최초 초기화 때 `ragdb`에만 적용됨)
- 청커를 고치면 `CHUNKER_VERSION`을 올리고 재수집해야 새 청크 기준으로 측정됨

## TODO / 미완료 작업
- q017 검색 실패는 dense 임베딩의 의미 혼동 문제. BM25+dense 하이브리드 검색이 다음 개선 후보 (질문은 바꾸지 않고 실패 사례로 남겨 둠)
- Anthropic 경로는 코드만 있고 실제로 돌려 본 적 없음 (API 크레딧 없음). 크레딧을 충전하면 `GENERATION_PROVIDER=anthropic`으로 같은 흐름을 다시 검증
- 다음 후보: GitHub Actions로 ruff + pytest CI (pgvector 서비스 컨테이너 필요)

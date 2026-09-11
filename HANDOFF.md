# HANDOFF

## Goal
자기소개서용 포트폴리오 프로젝트(RAG 문서 QA API). 평가셋 확장·검색 개선(2단계)과 Docker 전체 스택 검증(3단계)을 마친 뒤, 4단계로 하이브리드 검색(dense + Postgres 전문 검색, RRF)을 실험했다. 측정해 보니 평균이 더 나빠서 기본값은 dense로 유지했다.

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
- **하이브리드 검색 실험 (4단계)**:
  - `chunks.content_tsv`: Postgres가 관리하는 생성 컬럼(`to_tsvector('english', heading_path || content)`) + GIN 인덱스 (마이그레이션 0002). DB가 계산하므로 수집 코드는 바꾸지 않음
  - `hybrid_search` / `retrieve()` (`app/services/retrieval.py`), `RETRIEVAL_MODE` 설정(기본 `dense`), API와 두 평가 스크립트의 `--mode` 옵션
  - 30문항 결과: dense MRR 0.933(v3와 문항 단위까지 동일하므로 리팩터링으로 인한 동작 변화 없음) vs hybrid 0.898, Hit@10은 0.97 → 1.00. q017은 9위까지 올라오지만 q001, q009, q003이 밀림
  - 원인: `ts_rank`에 IDF가 없어서 "fastapi"(청크의 57%), "parameter"(28%) 같은 흔한 단어가 어휘 순위를 흐림. q009는 `release-notes.md`가 어휘 검색 1위였음. q017에서는 어휘 검색이 settings.md를 1위로 찾았지만 RRF를 거치며 희석됨
  - 기본값은 dense로 유지. 30문항에 맞춘 가중치 튜닝은 평가셋 과적합이 되므로 하지 않음

## Files touched
- 2단계: `app/services/chunking.py`, `app/services/ingestion.py`, `eval/qa_dataset.jsonl`, `eval/run_answer_eval.py`, `eval/reports/*`, `tests/test_chunking.py`, `README.md`
- 3단계: `.dockerignore`, `Dockerfile`, `docker-compose.yml`, `pyproject.toml`, `uv.lock`, `README.md`
- 4단계: `alembic/versions/0002_chunks_fulltext.py`, `app/models/chunk.py`, `app/services/retrieval.py`, `app/config.py`, `app/routers/query.py`, `eval/run_retrieval_eval.py`, `eval/run_answer_eval.py`, `tests/test_retrieval.py`, `.env.example`, `README.md`, `eval/reports/retrieval_eval_v4_*`

## Test results
- `ruff check .` 통과, `pytest` 25개 통과 (하이브리드 테스트 3개 추가: 어휘로만 걸리는 청크가 1위로 올라오는지, 불용어만 있는 질문, 검색할 단어가 없는 질문)
- `eval/reports/retrieval_eval_v4_dense_20260911_033421.md`: Hit@3 0.97, Hit@10 0.97, MRR 0.933
- `eval/reports/retrieval_eval_v4_hybrid_20260911_033439.md`: Hit@3 0.97, Hit@10 1.00, MRR 0.898
- 답변 품질은 기본값이 dense 그대로라 v3 리포트가 여전히 유효함: `eval/reports/answer_eval_v3_keep_definitions_20260910_222402.md` (키워드 커버리지 0.93, 충실도 4.17, 정확도 4.73)
- 클린 클론(`git clone` 후 `.env.example`만 복사): README 절차 그대로 빌드 → 빈 DB에 수집 155문서/915청크 → 데모 사용자 생성 → 로그인 → 인용이 붙은 답변 (3단계에서 확인)

## 환경 메모
- DB 컨테이너는 Docker Desktop이 재시작되면 내려갈 수 있음 → `docker compose up -d db`로 다시 올리면 됨. 데이터는 `pgdata` 볼륨에 남아 있음
- **Docker Desktop이 시작하자마자 죽는 경우**: `docker-desktop` WSL 배포판이 Stopped로 남고 오류 창에 "Quit / Reset to factory defaults"가 뜸. 백엔드 로그(`%LOCALAPPDATA%\Docker\log\host\com.docker.backend.exe.log`)의 마지막 `cancelling with error` 줄에 `rename ...sock ...sock.stale: The file cannot be accessed by the system`이 있으면, 비정상 종료로 남은 소켓 파일 때문임. 소켓 파일은 하나씩 지우거나 이름을 바꿀 수 없으므로, Docker Desktop을 종료한 뒤 그 파일이 든 폴더(`%LOCALAPPDATA%\Docker\run`, `%LOCALAPPDATA%\docker-secrets-engine`)를 `.stale-<날짜>`로 이름을 바꾸고 재시작하면 됨. **"Reset to factory defaults"는 볼륨(DB)을 지우므로 누르지 말 것**
- `ragdb_test`에는 `vector`, `pgcrypto` 확장을 직접 만들어 둬야 함 (`docker/postgres/init.sql`은 최초 초기화 때 `ragdb`에만 적용됨)
- 청커를 고치면 `CHUNKER_VERSION`을 올리고 재수집해야 새 청크 기준으로 측정됨

## TODO / 미완료 작업
- 기본값인 dense에서 q017은 여전히 실패함. 개선 후보는 IDF가 있는 BM25(예: ParadeDB의 `pg_search` 확장), 또는 튜닝 전용 검증 질문셋을 따로 만든 뒤 어휘 쪽 가중치를 조정하는 것
- Anthropic 경로는 코드만 있고 실제로 돌려 본 적 없음 (API 크레딧 없음). 크레딧을 충전하면 `GENERATION_PROVIDER=anthropic`으로 같은 흐름을 다시 검증
- 다음 후보: GitHub Actions로 ruff + pytest CI (pgvector 서비스 컨테이너 필요)
- `%LOCALAPPDATA%` 아래의 `*.stale-20260911*` 폴더들은 Docker 동작과 무관함. 정리하려면 재부팅한 뒤 삭제를 시도해 볼 것 (안의 소켓 파일 때문에 여전히 지워지지 않을 수 있음)

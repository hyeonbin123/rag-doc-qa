# HANDOFF

## Goal
자기소개서용 포트폴리오 프로젝트(RAG 문서 QA API). 평가셋 확장과 검색 개선(2단계)까지 완료했고, 다음 작업은 `docker compose up --build` 전체 스택 검증(3단계)이다.

## Done
- FastAPI 앱(auth/documents/query/logs/health), SQLAlchemy 모델 4종, Alembic 마이그레이션(pgvector + HNSW), 수집 파이프라인, 평가 하네스
- 생성 프로바이더 추상화: `GENERATION_PROVIDER=ollama`(기본, 로컬 Qwen2.5-7B) / `anthropic`. Ollama 경로는 답변(자유 텍스트)과 인용(숫자 스키마)을 2회 호출로 분리함 — 7B 모델이 제약 디코딩 중 문자열 속 따옴표를 이스케이프하지 못해 코드 답변이 잘렸기 때문
- GitHub 공개 저장소: https://github.com/hyeonbin123/rag-doc-qa (초기 커밋 `27af02d`)
- **평가셋 5 → 30문항** (`eval/qa_dataset.jsonl`): 실제 수집된 코퍼스 내용을 읽고 작성했고, 참조한 `expected_source_paths`가 DB에 모두 있는지 확인함
- **검색 개선 v1 → v2 → v3** (30문항, MRR 0.828 → 0.911 → 0.933)
  - v2: `clean_markdown()` 추가 — MkDocs 헤딩 앵커 `{ #id }`, 코드 include 지시문 `{* ... *}`, admonition 구분자, HTML 태그 제거 (코드 펜스와 인라인 코드는 건드리지 않음)
  - v3: v2가 `<dfn title="...">`의 정의 텍스트까지 지워 q011이 회귀함 → `<dfn>`/`<abbr>`는 "용어 (정의)"로 보존
- **잠재 버그 수정**: 수집 해시가 원문만 봐서 청커를 바꿔도 전체가 "변경 없음"으로 스킵됐음 → `CHUNKER_VERSION`을 해시에 포함 (`app/services/ingestion.py`)
- **평가 버그 수정**: 판정 점수 범위가 설명에만 있어서 로컬 판정 모델이 10점 척도로 넘어감(평균 9.17) → 스키마에 `minimum`/`maximum` 추가, 범위를 벗어나면 `ValueError`로 평가 실패, 리포트에 문항별 표 추가 (`eval/run_answer_eval.py`). 무효 측정인 v2 답변 리포트는 삭제함

## Files touched (2단계)
- `app/services/chunking.py`: `clean_markdown`, `strip_heading_anchor`, `CHUNKER_VERSION`
- `app/services/ingestion.py`: 해시에 청커 버전 포함, 제목에서 앵커 제거
- `eval/qa_dataset.jsonl`, `eval/run_answer_eval.py`, `eval/reports/*`
- `tests/test_chunking.py`: 정제 관련 테스트 6개 추가
- `README.md`: 측정 결과를 30문항 v1→v3 기준으로 교체, 알려진 한계 섹션 추가

## Test results
- `ruff check .` 통과, `pytest` 22개 통과
- `eval/reports/retrieval_eval_v3_keep_definitions_20260910_221511.md`: Hit@3 0.97, Hit@10 0.97, MRR 0.933
- `eval/reports/answer_eval_v3_keep_definitions_20260910_222402.md`: 키워드 커버리지 0.93, 충실도 4.17, 정확도 4.73, 판정 환각 1/30 (q017의 올바른 거절 응답을 판정 모델이 잘못 분류한 것)

## 환경 메모
- DB 컨테이너는 Docker Desktop이 재시작되면 내려갈 수 있음 → `docker compose up -d db`. 데이터는 `pgdata` 볼륨에 남아 있음
- `ragdb_test`에는 `vector`, `pgcrypto` 확장을 수동으로 만들어 둬야 함 (`docker/postgres/init.sql`은 최초 초기화 때 `ragdb`에만 적용됨)
- 청커를 수정하면 `CHUNKER_VERSION`을 올린 뒤 재수집해야 새 청크로 측정됨

## TODO / 미완료 작업
- **3단계 (다음 작업)**: `docker compose up --build`로 API 컨테이너까지 포함한 전체 스택 검증. 컨테이너 안에서는 `DATABASE_URL`이 `localhost`가 아니라 `db` 서비스를, `OLLAMA_BASE_URL`은 `host.docker.internal:11434`를 가리켜야 함. Dockerfile의 CPU torch 인덱스 설정과 임베딩 모델 사전 다운로드도 실제 빌드로 확인 필요
- q017 검색 실패는 dense 임베딩의 의미 혼동 — BM25+dense 하이브리드 검색이 다음 개선 후보 (질문은 바꾸지 않고 실패 사례로 유지)
- Anthropic 경로는 코드만 있고 실행 검증 안 됨 (API 크레딧 없음). 충전하면 `GENERATION_PROVIDER=anthropic`으로 같은 플로우를 재검증

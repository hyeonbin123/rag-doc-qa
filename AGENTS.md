# rag-doc-qa 프로젝트 규칙

먼저 상위 워크스페이스 규칙 `../AGENTS.md`를 읽는다. 이 파일은 이 프로젝트에만 해당하는 추가 규칙이다.

## 개요
FastAPI 공식 문서를 코퍼스로 하는 RAG 기반 문서 QA API 서버. 상세 설계는 `README.md`와 최초 설계 시점의 계획 문서를 참고한다.

## 스택
- Python 3.11, FastAPI, SQLAlchemy 2.0(비동기), Alembic
- PostgreSQL 16 + pgvector (Docker Compose로 실행)
- 임베딩: 로컬 `BAAI/bge-small-en-v1.5` (sentence-transformers)
- 생성: Claude API (Anthropic), tool-use로 인용 구조화
- 의존성 관리: uv (`pyproject.toml` + `uv.lock`)

## 작업 규칙
- 스크래치 파일은 `work/`에 둔다.
- 스키마를 바꿀 때는 `app/models/*`와 `alembic/versions/*` 마이그레이션을 함께 수정한다.
- 청킹 로직(`app/services/chunking.py`)은 앱과 `scripts/ingest_fastapi_docs.py`가 공유하므로 한쪽만 고치지 않는다.
- 커밋 전 `pytest`와 관련 있는 경우 `eval/run_retrieval_eval.py` / `eval/run_answer_eval.py`를 실행해 회귀를 확인한다.
- `.env`에는 `ANTHROPIC_API_KEY` 등 실제 비밀값을 두고 절대 커밋하지 않는다. 예시는 `.env.example`에만 둔다.
- 담당이 바뀔 때 `HANDOFF.md`를 갱신한다 (목표/완료 내용/수정 파일/테스트 결과/미완료 작업).

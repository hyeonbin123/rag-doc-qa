# HANDOFF

## Goal
자기소개서용 포트폴리오 프로젝트(RAG 문서 QA API, 1주차 분량) 스캐폴딩 완료.

## Done
- 전체 디렉터리 구조 생성 (app/, alembic/, scripts/, eval/, tests/, docker/)
- FastAPI 앱: auth(JWT)/documents(ingest)/query(ask)/logs/health 라우터 구현
- SQLAlchemy 모델 4종(User, Document, Chunk, QueryLog) + Alembic 초기 마이그레이션(pgvector+hnsw 인덱스 포함)
- 마크다운 청킹 서비스(`app/services/chunking.py`) — 헤딩 추적 + 코드펜스 보호 + 토큰 윈도잉, 단위 테스트 6개 통과
- FastAPI 공식 문서 수집 파이프라인(`app/services/ingestion.py`, idempotent) + CLI 스크립트
- 로컬 임베딩(BGE-small) / Claude tool-use 생성 서비스 구현
- 평가 하네스 골격(`eval/run_retrieval_eval.py`, `eval/run_answer_eval.py`) + 스타터 QA 데이터셋 5문항(추후 25~30개로 확장 필요)
- Dockerfile / docker-compose.yml / README 작성
- `uv sync` 성공, `ruff check .` 전부 통과, `app.main` 임포트 성공 확인
- git 저장소 초기화 및 파일 스테이징 완료 (아직 커밋은 안 함 — 사용자 확인 대기)
- WSL2 + Docker Desktop 설치 및 실행 확인 (winget 설치, 엔진 정상)
- `docker compose up -d db` 정상 기동(healthy), `alembic upgrade head`로 실제 pgvector DB에 스키마 적용 확인
- `scripts.ingest_fastapi_docs` 실전 실행 성공: FastAPI 공식 문서 155개 → 청크 971개 생성 (GitHub repo가 `tiangolo/fastapi`에서 이전되어 301 리다이렉트가 발생했던 문제를 `httpx.AsyncClient(follow_redirects=True)`로 수정)
- 로컬 uvicorn으로 `/health`, `/auth/register`, `/auth/login`, `/query/ask` 실제 호출 검증 — 인증과 검색(retrieval)까지는 완전히 정상 동작 확인
- `ragdb_test` DB 생성(vector/pgcrypto 확장 활성화) 후 **pytest 통합 스위트 16개 전체 통과** (auth 5, chunking 6, query 3, retrieval 2)
- 실제 데이터로 **retrieval eval 실행 완료**: Hit@3/5/10 = 1.00, MRR = 0.800 (`eval/reports/retrieval_eval_v1_baseline_20260910_165812.md`) — 5문항 모두 정답 문서를 top-10 안에서 찾음

## Files touched
- rag-doc-qa/ 전체 신규 생성 (64개 파일)
- `app/services/ingestion.py`, `scripts/fetch_docs.py`: httpx `follow_redirects=True` 추가 (GitHub repo 이전 대응)
- `eval/reports/retrieval_eval_v1_baseline_20260910_165812.md`: 첫 baseline 리포트 생성됨

## Test results
- `ruff check .` 통과, `pytest` 전체 16개 통과
- `eval/run_retrieval_eval.py --tag v1_baseline`: Hit@3/5/10 = 1.00, MRR = 0.800
- `eval/run_answer_eval.py --tag v1_local_qwen` (로컬 Qwen 생성 + 로컬 Qwen 판정): 키워드 커버리지 0.80, 충실도 4.20/5, 정확도 4.60/5, 환각 0/5
- `/query/ask` 실제 호출 성공: 코드 블록 포함 완전한 답변 + 정답 문서 인용, 총 4.6초 (임베딩 44ms / 검색 30ms / 생성 4.5s)

## LLM 프로바이더 전환 (2026-09-11)
Anthropic 계정 크레딧 부족으로 막혔던 문제를 **프로바이더 추상화**로 해결함. 비용 0원으로 전체 파이프라인이 동작한다.
- `GenerationService`를 ABC로 바꾸고 `AnthropicGenerationService` / `OllamaGenerationService` 두 구현 추가, `GENERATION_PROVIDER` 설정으로 스위칭 (`app/services/generation.py`)
- Ollama 0.34.0 + `qwen2.5:7b-instruct` 설치, RTX 2080 Ti에서 100% GPU 로드(VRAM 5.9/11.2GB), 워밍업 후 약 85 tok/s
- **발견한 이슈와 해결**: 로컬 7B 모델은 JSON 스키마 제약 디코딩 중 문자열 안 따옴표를 이스케이프하지 못해, 코드가 포함된 답변이 첫 `"`에서 잘렸음. Ollama 경로만 답변 생성(자유 텍스트) + 인용 추출(숫자 스키마) 2회 호출로 분리해 해결. Claude 경로는 1회 tool-use 호출 유지.
- Ollama 기본 컨텍스트 4096이 검색 결과만으로 거의 차서 `num_ctx=8192`, `num_predict=1024`로 조정
- `citations` 스키마에 `minItems: 1` 추가 — 없으면 작은 모델이 빈 배열로 스키마를 만족시켜버림
- eval 판정 LLM도 프로바이더를 따라가도록 변경(`run_answer_eval.py`) → 평가 전체가 무료로 실행 가능

## TODO / 미완료 작업
- `eval/qa_dataset.jsonl`을 25~30문항으로 확장 필요 (현재 5문항 스타터셋)
- q004("dependency injection")는 키워드 커버리지 0.00 — 모델이 개념은 맞게 설명하지만 `Depends`라는 정확한 토큰을 안 씀. 키워드 기준을 고칠지, 프롬프트를 조정할지 판단 필요 (eval 개선 사례로 쓸 만함)
- v2 튜닝 실험(청크 크기/top_k 변경 후 재측정)해서 v1 대비 비교 리포트 만들기 — 자기소개서의 "측정하고 개선했다" 근거
- git 초기 커밋 여부는 사용자 확인 후 진행 (git init/staging은 완료된 상태)
- Docker Desktop을 통한 `docker compose up --build`(API 컨테이너 포함) 전체 스택은 아직 미검증 — 지금까지는 `db` 서비스만 컨테이너로 띄우고 API는 로컬 uv 환경에서 직접 실행함. Dockerfile은 Anthropic 기준으로 작성돼 있어 Ollama 사용 시 컨테이너에서 호스트 Ollama에 접근하려면 `host.docker.internal` 설정이 필요함 (미반영)
- Anthropic 크레딧 충전 시: `.env`에서 `GENERATION_PROVIDER=anthropic`으로 바꾸고 동일 플로우 재검증하면 Claude 경로도 확인 가능

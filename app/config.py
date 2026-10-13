# [파일 역할] 앱 전체의 설정값을 한 클래스(Settings)로 모은다. DB 주소, JWT, 생성 모델(Ollama/Claude), 언어별
# 임베딩·재정렬 모델, 검색 모드, 모델 스레드 수, 관리자 적재 토큰이 여기 있다.
# [왜 이 방식인가] pydantic-settings는 환경 변수와 .env 파일을 읽어 타입을 검사하고 기본값을 채운다. 그래서
# 같은 코드가 호스트(.env의 localhost)와 컨테이너(compose가 덮어쓴 DATABASE_URL, OLLAMA_BASE_URL)에서 설정만
# 바꿔 돈다. 잘못된 값(예: RETRIEVAL_MODE=foo)은 시작할 때 바로 오류가 난다.
# [연결] get_settings()로 앱 곳곳(DB 세션, 보안, 임베딩, 재정렬, 생성, 스레드 풀)과 Alembic(alembic/env.py),
# 평가 스크립트가 같은 인스턴스를 읽는다. 각 기본값의 근거는 아래 기존 영어 주석과 docs/experiments.md에 있다.

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


# 설정 모델. 필드 이름의 대문자 형태가 환경 변수 이름이다(예: retrieval_mode ↔ RETRIEVAL_MODE).
class Settings(BaseSettings):
    # env_file=".env": 현재 작업 폴더의 .env를 읽는다(실제 환경 변수가 있으면 그쪽이 우선). extra="ignore":
    # .env에는 compose만 쓰는 POSTGRES_USER 같은 키도 있으므로 모르는 키가 있어도 오류를 내지 않는다.
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # 기본값이 없는 필수 설정. DB 주소와 JWT 서명 키가 없으면 Settings()를 만들 때 검증 오류로 앱이 뜨지
    # 않는다.
    # 토큰 수명: 접근 토큰 30분, 갱신 토큰 7일(/auth/refresh로 접근 토큰만 새로 받는다).
    database_url: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # 답변 생성기 선택. 기본은 비용 없이 반복할 수 있는 로컬 Ollama다(README '로컬 모델'). anthropic이면
    # Claude API를 쓰며 anthropic_api_key가 필요하다. README에 따르면 Claude 경로는 단위 테스트만 있고 실제
    # API로는 돌려 보지 않았다.
    generation_provider: Literal["anthropic", "ollama"] = "ollama"
    anthropic_api_key: str = ""
    claude_model_name: str = "claude-sonnet-5"
    # Ollama 서버 주소. 호스트에서 실행하는 기준값이고, 컨테이너 안에서는 compose가
    # host.docker.internal:11434로 덮어쓴다.
    ollama_base_url: str = "http://localhost:11434"
    # A.X-4.0-Light (Q4_K_M), built locally with scripts/ax40_light/; adopted in v13 over
    # qwen2.5:7b-instruct, which stays the judge (docs/experiments.md v13).
    ollama_model_name: str = "a.x-4.0-light:q4_k_m"
    # Sent as Ollama's `think` field when set; models that reason by default (qwen3.5)
    # need false. Unset sends no field, as before v13 (docs/experiments.md).
    ollama_think: bool | None = None
    # Regenerate once a Korean answer that slipped into Chinese or Japanese (v13; on since
    # the v13 adoption).
    language_guard: bool = True
    # 영어 문서·질문 임베딩 모델. v8에서 다국어 모델 하나로 통일하면 영어 테스트셋 MRR이 0.933 → 0.638로
    # 떨어져 영어는 이 모델을 유지했다(docs/experiments.md v8).
    embedding_model_name: str = "BAAI/bge-small-en-v1.5"
    # Korean docs and questions need a multilingual model; English keeps the English
    # one because the multilingual model scored far lower on the English test sets.
    # Granite R2 311M cut to 384 dimensions, adopted in v13 stage B over
    # intfloat/multilingual-e5-small, which stays in the image (docs/experiments.md).
    embedding_model_name_ko: str = "ibm-granite/granite-embedding-311m-multilingual-r2"
    # 검색 방식. dense(벡터만), hybrid(벡터 + SQL BM25를 가중 RRF로 합침), rerank(두 후보를 cross-encoder로
    # 다시 채점). 기본 dense는 v7(영어)·v9(한국어)에서 미리 정한 규칙으로 확정한 값이다. 나머지 두 모드는
    # 설정으로 켤 수 있게 남겨 두었다.
    retrieval_mode: Literal["dense", "hybrid", "rerank"] = "dense"
    # rerank 모드에서 영어 질문에 쓰는 cross-encoder. v6에서 지연 예산(검색 중앙값 1초) 안에 드는 모델로
    # 골랐다(docs/experiments.md v6).
    reranker_model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    # The model above was trained on English only; on the Korean tuning set it ranked
    # worse than no reranking at all, so Korean questions get a multilingual one.
    reranker_model_name_ko: str = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"
    # Worker threads for CPU-bound model calls (embeddings, the cross-encoder). 6 was
    # measured against 1 on a 12-core desktop; see app/services/inference.py.
    model_threads: int = 6
    # fastapi_docs_commit_sha: .env.example에도 있는 키지만 지금 코드에서 이 필드를 읽는 곳은 없다. 적재
    # 커밋은 요청·명령의 commit_sha(또는 --commit)로 정하고, 없으면 tiangolo/fastapi master 브랜치의 최신
    # 커밋을 쓴다(app/services/ingestion.py의 resolve_commit_sha).
    # admin_ingest_token: 관리자 적재 API(/admin/documents/ingest)의 X-Admin-Token 헤더와 비교하는
    # 값(app/dependencies.py의 require_admin_token). 기본값은 비어 있고, 비어 있거나 예전 공개 예시
    # 값('change-me-admin-token')이면 관리자 적재 API가 꺼진다(403). 쓰려면 .env에 추측할 수 없는 값을 넣는다.
    fastapi_docs_commit_sha: str = ""
    admin_ingest_token: str = ""

    # 질문·문서 언어 → 임베딩 모델 이름. 'ko'만 한국어 모델이고 나머지는 영어 모델이다.
    # get_embedding_service(app/services/embedding.py)가 이것으로 어느 모델을 올릴지 정한다.
    def embedding_model_for(self, language: str) -> str:
        return self.embedding_model_name_ko if language == "ko" else self.embedding_model_name

    # 질문 언어 → cross-encoder 이름. get_reranker_service(app/services/reranking.py)와
    # eval/run_retrieval_eval.py가 쓴다.
    def reranker_model_for(self, language: str) -> str:
        return self.reranker_model_name_ko if language == "ko" else self.reranker_model_name


# Settings를 프로세스당 한 번만 만들어 재사용한다(.env를 매 요청 다시 읽지 않는다). FastAPI의
# Depends(get_settings)로도 주입된다. 설정을 바꿔 다시 읽어야 하는 테스트는 get_settings.cache_clear()를
# 부른다(tests/test_generation.py).
@lru_cache
def get_settings() -> Settings:
    return Settings()

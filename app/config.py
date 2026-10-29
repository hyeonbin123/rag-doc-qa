# [파일 역할] 앱 전체의 설정값을 한 클래스(Settings)로 모은다. DB 주소, JWT, 생성 모델(Ollama/Claude), 언어별
# 임베딩·재정렬 모델, 검색 모드, 모델 스레드 수, 관리자 적재 토큰이 여기 있다.
# [왜 이 방식인가] pydantic-settings는 환경 변수와 .env 파일을 읽어 타입을 검사하고 기본값을 채운다. 그래서
# 같은 코드가 호스트(.env의 localhost)와 컨테이너(compose가 덮어쓴 DATABASE_URL, OLLAMA_BASE_URL)에서 설정만
# 바꿔 돈다. 잘못된 값(예: RETRIEVAL_MODE=foo, MODEL_THREADS=0, JWT_ALGORITHM=RS256)은 시작할 때 바로 오류가
# 난다. 타입만이 아니라 범위(1 이상, 허용 목록)도 필드에 적어 두어, 첫 요청에서 500으로 드러나지 않게 한다.
# [연결] get_settings()로 앱 곳곳(DB 세션, 보안, 임베딩, 재정렬, 생성, 스레드 풀)과 Alembic(alembic/env.py),
# 평가 스크립트가 같은 인스턴스를 읽는다. 각 기본값의 근거는 아래 기존 영어 주석과 docs/experiments.md에 있다.

import logging
from functools import lru_cache
from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

# JWT 비밀키로 받지 않는 값: 이 저장소에 공개된 문자열. 저장소가 공개라 누구나 아는 값이고, 이 값으로
# 서명하면 사용자 UUID만 알아도 그 사용자의 토큰을 만들 수 있다(관리자 토큰의 PLACEHOLDER_ADMIN_TOKENS와 같은
# 생각, app/dependencies.py).
# - change-me-to-a-random-secret: .env.example의 예시 값.
# - ci-only-secret-not-used-by-any-deployment: CI 워크플로(.github/workflows/ci.yml)가 테스트에 쓰는 값.
#   41바이트라 길이 검사만으로는 걸리지 않아 따로 적는다. CI는 APP_ENV를 두지 않으므로(development) 이
#   값이어도 경고만 나고 테스트는 그대로 돈다(tests/test_security.py가 워크플로 파일에서 값을 읽어 이 목록과
#   맞춰 본다).
PUBLIC_EXAMPLE_JWT_SECRETS = frozenset(
    {"change-me-to-a-random-secret", "ci-only-secret-not-used-by-any-deployment"}
)
# 서명 알고리즘별 비밀키 최소 길이(바이트) = 그 알고리즘의 해시 출력 길이. 이보다 짧은 HMAC 키는 RFC 7518
# 3.2절이 금지하고, PyJWT도 같은 기준(hash_alg().digest_size)으로 InsecureKeyLengthWarning을 낸다. 키는 아래
# Settings.jwt_algorithm의 허용 목록(HS256·HS384·HS512)과 같아야 한다.
MIN_JWT_SECRET_BYTES_BY_ALGORITHM = {"HS256": 32, "HS384": 48, "HS512": 64}
# 기본 알고리즘 HS256(HMAC-SHA256)의 최소 길이. 알고리즘을 따로 주지 않은 검사가 쓴다.
MIN_JWT_SECRET_BYTES = MIN_JWT_SECRET_BYTES_BY_ALGORITHM["HS256"]


# JWT 비밀키의 문제를 사람이 읽을 문장으로 돌려준다(문제가 없으면 None). 비어 있음, 저장소에 공개된 값, 서명
# 알고리즘의 최소 길이 미만을 본다. algorithm을 주지 않으면 기본값 HS256 기준(32바이트)이다. 앞뒤 공백은 떼고
# 비교한다(.env에서 실수로 붙은 공백 때문에 검사를 피하지 않게). 목록에 없는 알고리즘 이름이면 HS256 기준으로
# 보는데, Settings는 그런 이름을 먼저 거부하므로 설정에서 오는 값으로는 생기지 않는다.
def jwt_secret_problem(secret: str, algorithm: str = "HS256") -> str | None:
    stripped = secret.strip()
    if not stripped:
        return "JWT_SECRET_KEY is empty"
    if stripped in PUBLIC_EXAMPLE_JWT_SECRETS:
        return "JWT_SECRET_KEY is a public value from this repository (.env.example or the CI workflow)"
    minimum = MIN_JWT_SECRET_BYTES_BY_ALGORITHM.get(algorithm, MIN_JWT_SECRET_BYTES)
    if len(secret.encode("utf-8")) < minimum:
        return f"JWT_SECRET_KEY is shorter than {minimum} bytes, the minimum for {algorithm}"
    return None


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
    # 실행 환경. development(기본)는 JWT 비밀키가 약해도(빈 값, 공개 예시 값, 32바이트 미만) 큰 경고만 남기고
    # 시작한다. 지금 로컬에서 .env.example을 그대로 복사해 쓰는 실행을 깨지 않기 위해서다. production이면 같은
    # 경우에 설정 검증 오류로 시작하지 않는다(아래 _refuse_weak_secret_in_production). 바깥에 여는 배포는
    # production으로 두고 비밀키를 python -c "import secrets; print(secrets.token_urlsafe(48))" 같은 값으로
    # 바꾼다.
    # production이면 FastAPI의 문서 페이지(/docs, /redoc)도 끈다(app/main.py의 docs_page_urls).
    app_env: Literal["development", "production"] = "development"
    # 서명 알고리즘은 문자열 비밀키를 쓰는 HMAC-SHA2 세 가지만 받는다. 예전에는 str이라 RS256 같은 값도 받아
    # 서버는 뜨지만 첫 로그인에서 서명이 실패해 500이 됐다(비대칭 알고리즘은 문자열 키로 서명할 수 없다).
    # 비밀키 최소 길이는 고른 알고리즘을 따른다(위 MIN_JWT_SECRET_BYTES_BY_ALGORITHM).
    jwt_algorithm: Literal["HS256", "HS384", "HS512"] = "HS256"
    # 토큰 수명은 1 이상만 받는다. 0이나 음수면 발급하자마자 만료된 토큰이 나와 로그인해도 모든 인증 요청이
    # 401이 됐다.
    access_token_expire_minutes: int = Field(30, ge=1)
    refresh_token_expire_days: int = Field(7, ge=1)

    # 답변 생성기 선택. 기본은 비용 없이 반복할 수 있는 로컬 Ollama다(README '로컬 모델'). anthropic이면
    # Claude API를 쓰며 anthropic_api_key가 필요하다. README에 따르면 Claude 경로는 단위 테스트만 있고 실제
    # API로는 돌려 보지 않았다.
    generation_provider: Literal["anthropic", "ollama"] = "ollama"
    anthropic_api_key: str = ""
    claude_model_name: str = "claude-sonnet-5"
    # Ollama 서버 주소. 호스트에서 실행하는 기준값이고, 컨테이너 안에서는 compose가
    # host.docker.internal:11434로 덮어쓴다.
    ollama_base_url: str = "http://localhost:11434"
    # 기본 생성 모델 A.X-4.0-Light(Q4_K_M). scripts/ax40_light/로 직접 GGUF로 변환해 만들었고, v13에서
    # qwen2.5:7b-instruct 대신 채택했다. qwen2.5:7b-instruct는 답변 판정 모델로 계속 쓴다
    # (docs/experiments.md v13).
    ollama_model_name: str = "a.x-4.0-light:q4_k_m"
    # 값이 있으면 Ollama 요청의 `think` 필드로 보낸다. 기본으로 추론 과정을 내는 모델(qwen3.5)은 false가
    # 필요하다. 비워 두면(None) v13 이전처럼 이 필드를 아예 보내지 않는다(docs/experiments.md).
    ollama_think: bool | None = None
    # 언어 가드: 한국어 답변이 중국어나 일본어로 새면 한 번 다시 생성한다(v13에서 도입, v13 채택 때부터
    # 켜 둠).
    language_guard: bool = True
    # v15 후보 세 가지(docs/experiments.md v15). 기본값은 모두 지금 동작이고, 측정으로 채택이 정해지기 전에는
    # 바꾸지 않는다. 자세한 동작은 app/services/generation.py.
    # - citation_mode: separate(기본)는 인용을 다른 프롬프트로 따로 부른다. followup은 답변 대화에 이어 붙여
    #   프롬프트 캐시를 다시 쓰고 정수 배열로 받는다(인용 호출 시간을 줄이려는 후보).
    # - refuse_without_context: 검색된 청크가 0개면 LLM 없이 고정 거절문을 돌려준다(바닥값으로 청크가 다
    #   걸러졌을 때 지어낸 답을 막는 후보).
    # - empty_citations_on_refusal: '문서에 내용이 없다'는 거절 답에는 인용을 붙이지 않는다. v15 I4에서 채택해
    #   2026-10-18부터 기본으로 켬(dev에서 잘 답한 답을 거절로 잘못 분류한 경우가 언어별 1개 이하였고, 답 없는
    #   test 질문의 거절 답 27개에 붙던 인용이 모두 사라짐). 나머지 둘은 측정에서 채택되지 않아 꺼진 채로 둠.
    citation_mode: Literal["separate", "followup"] = "separate"
    refuse_without_context: bool = False
    empty_citations_on_refusal: bool = True
    # 영어 문서·질문 임베딩 모델. v8에서 다국어 모델 하나로 통일하면 영어 테스트셋 MRR이 0.933 → 0.638로
    # 떨어져 영어는 이 모델을 유지했다(docs/experiments.md v8).
    embedding_model_name: str = "BAAI/bge-small-en-v1.5"
    # 한국어 문서·질문 임베딩 모델. 한국어에는 다국어 모델이 필요하지만, 다국어 모델은 영어 테스트셋 점수가
    # 훨씬 낮아 영어는 위의 영어 전용 모델을 그대로 쓴다. 지금 값은 Granite R2 311M을 384차원으로 잘라 쓴
    # 것으로, v13 단계 B에서 intfloat/multilingual-e5-small 대신 채택했다. e5-small도 이미지에 그대로 남아
    # 있다(docs/experiments.md).
    embedding_model_name_ko: str = "ibm-granite/granite-embedding-311m-multilingual-r2"
    # 검색 방식. dense(벡터만), hybrid(벡터 + SQL BM25를 가중 RRF로 합침), rerank(두 후보를 cross-encoder로
    # 다시 채점). 기본 dense는 v7(영어)·v9(한국어)에서 미리 정한 규칙으로 확정한 값이다. 나머지 두 모드는
    # 설정으로 켤 수 있게 남겨 두었다.
    retrieval_mode: Literal["dense", "hybrid", "rerank"] = "dense"
    # rerank 모드에서 영어 질문에 쓰는 cross-encoder. v6에서 지연 예산(검색 중앙값 1초) 안에 드는 모델로
    # 골랐다(docs/experiments.md v6).
    reranker_model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    # 위 모델은 영어로만 학습돼, 한국어 튜닝용 셋에서는 재정렬을 아예 안 한 것보다도 순위를 못 매겼다. 그래서
    # 한국어 질문에는 다국어 cross-encoder를 쓴다(docs/experiments.md v9).
    reranker_model_name_ko: str = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"
    # CPU를 쓰는 모델 호출(임베딩, cross-encoder)을 돌리는 작업 스레드 수. 12코어 데스크톱에서 6개와 1개를
    # 비교해 6으로 정했다. 자세한 근거는 app/services/inference.py. 1 이상만 받는다. 스레드 풀은 첫 질문 때
    # 만들어지므로, 예전에는 0 이하 값이 시작·/health를 통과한 뒤 첫 /query/ask에서 ValueError(500)로
    # 드러났다.
    model_threads: int = Field(6, ge=1)
    # fastapi_docs_commit_sha: 적재 요청·명령이 commit_sha(--commit)를 주지 않았을 때 적재할
    # tiangolo/fastapi의 ref(브랜치·태그·커밋 SHA). 비어 있으면(기본) 측정에 쓴 문서 스냅숏 커밋 50113da를
    # 쓴다(app/services/ingestion.py의 DOCS_SNAPSHOT_COMMIT·default_commit_ref). 최신 문서를 늘 받으려면
    # master를 넣는다. 어느 값이든 적재가 GitHub에 물어 40자 SHA로 바꾼 뒤 쓴다. 2026-10-29 전에는 코드가 이
    # 필드를 읽지 않았고 기본 적재 대상은 master의 최신 커밋이었다.
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

    # APP_ENV=production일 때만 약한 JWT 비밀키를 거부한다. ValueError는 pydantic의 ValidationError가 되어
    # Settings()가 실패하므로, uvicorn 시작(app/main.py)과 Alembic(alembic/env.py)이 모두 멈춘다. 최소 길이는
    # 설정한 서명 알고리즘 기준이다(HS512면 64바이트).
    @model_validator(mode="after")
    def _refuse_weak_secret_in_production(self) -> "Settings":
        problem = jwt_secret_problem(self.jwt_secret_key, self.jwt_algorithm)
        if self.app_env == "production" and problem:
            raise ValueError(f"{problem}; refusing to start with APP_ENV=production")
        return self


# 개발 모드에서 JWT 비밀키가 약하면 눈에 띄는 경고를 남기고 True를 돌려준다(괜찮으면 False). 서버 시작 때
# app/main.py의 lifespan이 한 번 부른다. 값 자체는 로그에 쓰지 않는다. 안내하는 최소 길이는 설정한 서명
# 알고리즘 기준이다. 예시 명령의 token_urlsafe(48)은 64자(64바이트)라 HS512 기준도 넘는다.
def warn_if_weak_jwt_secret(settings: Settings) -> bool:
    problem = jwt_secret_problem(settings.jwt_secret_key, settings.jwt_algorithm)
    if problem is None:
        return False
    logger.warning(
        "\n%s\nINSECURE: %s. Anyone who knows it can forge login tokens for this server.\n"
        "Set JWT_SECRET_KEY in .env to a random value of at least %d bytes, e.g.\n"
        '  python -c "import secrets; print(secrets.token_urlsafe(48))"\n'
        "(existing tokens stop working; log in again). APP_ENV=production refuses to start "
        "with such a key.\n%s",
        "=" * 78,
        problem,
        MIN_JWT_SECRET_BYTES_BY_ALGORITHM.get(settings.jwt_algorithm, MIN_JWT_SECRET_BYTES),
        "=" * 78,
    )
    return True


# Settings를 프로세스당 한 번만 만들어 재사용한다(.env를 매 요청 다시 읽지 않는다). FastAPI의
# Depends(get_settings)로도 주입된다. 설정을 바꿔 다시 읽어야 하는 테스트는 get_settings.cache_clear()를
# 부른다(tests/test_generation.py).
@lru_cache
def get_settings() -> Settings:
    return Settings()

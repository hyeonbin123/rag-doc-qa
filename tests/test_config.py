# [테스트 묶음] app/config.py의 Settings가 범위를 벗어난 설정값을 만들 때 바로 거부하는지 확인한다.
# [왜 중요한가] pydantic-settings는 타입만 검사하므로, 예전에는 MODEL_THREADS=0, JWT_ALGORITHM=RS256,
# ACCESS_TOKEN_EXPIRE_MINUTES=0 같은 값도 그대로 받았다. 그러면 서버는 뜨고 /health도 200인데 나중에
# 터졌다.
# - MODEL_THREADS가 0 이하: 첫 /query/ask에서 ThreadPoolExecutor(max_workers=0)가 ValueError → 500
#   (app/services/inference.py, 스레드 풀은 처음 쓸 때 만든다).
# - JWT_ALGORITHM이 HMAC이 아님(RS256 등): 문자열 비밀키로는 서명할 수 없어 첫 로그인이 500(이 프로젝트
#   의존성에는 cryptography가 없어 PyJWT가 NotImplementedError를 낸다).
# - 토큰 수명이 0 이하: 발급하자마자 만료된 토큰이 나와 로그인해도 모든 인증 요청이 401.
# 이제는 Settings()를 만들 때 ValidationError가 나서 uvicorn·Alembic이 시작하지 않고, 오류에 어느 설정이
# 틀렸는지 나온다(RETRIEVAL_MODE=foo가 원래 시작 때 거부되던 것과 같은 방식).
# [격리] _env_file=None으로 저장소의 .env를 읽지 않고 필수 값(database_url, jwt_secret_key)만 직접 준다.
# 환경 변수 경로는 monkeypatch.setenv로 따로 확인한다(실제 배포는 .env·환경 변수로 값을 넣으므로).

# jwt: PyJWT. 허용한 알고리즘이 모두 문자열 비밀키로 서명·검증되는지 볼 때만 쓴다.
import jwt
import pytest
from pydantic import ValidationError

from app.config import Settings

# 필수 설정 두 개. 비밀키는 HS512 기준(64바이트)도 넘는 길이로 둬, 키 길이 검사와 섞이지 않게 한다.
REQUIRED = {"database_url": "x", "jwt_secret_key": "k" * 64}


# .env를 읽지 않는 Settings. overrides로 시험할 값을 넣는다.
def make_settings(**overrides) -> Settings:
    return Settings(_env_file=None, **REQUIRED, **overrides)


# ValidationError가 정확히 그 필드 하나에서, 기대한 규칙(type)으로 났는지 본다. 다른 이유(필수 값 누락 등)로
# 실패한 것을 범위 검사로 착각하지 않게 하려는 것이다.
def assert_rejected(excinfo: pytest.ExceptionInfo[ValidationError], field: str, error_type: str) -> None:
    errors = excinfo.value.errors()
    assert [(error["loc"], error["type"]) for error in errors] == [((field,), error_type)]


# 기본값은 그대로다(지금 동작을 바꾸지 않는다): 스레드 6개, 접근 토큰 30분, 갱신 토큰 7일, HS256.
def test_the_defaults_are_unchanged():
    settings = make_settings()

    assert settings.model_threads == 6
    assert settings.access_token_expire_minutes == 30
    assert settings.refresh_token_expire_days == 7
    assert settings.jwt_algorithm == "HS256"


# 개수·수명 설정은 1 이상만 받는다. 0과 음수는 시작할 때 거부된다.
@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("model_threads", 0),
        ("model_threads", -1),
        ("access_token_expire_minutes", 0),
        ("access_token_expire_minutes", -30),
        ("refresh_token_expire_days", 0),
        ("refresh_token_expire_days", -7),
    ],
)
def test_counts_and_lifetimes_below_one_are_refused(field, value):
    with pytest.raises(ValidationError) as excinfo:
        make_settings(**{field: value})

    assert_rejected(excinfo, field, "greater_than_equal")


# 하한 1은 받는다(경계값).
def test_counts_and_lifetimes_of_one_are_accepted():
    settings = make_settings(model_threads=1, access_token_expire_minutes=1, refresh_token_expire_days=1)

    assert settings.model_threads == 1
    assert settings.access_token_expire_minutes == 1
    assert settings.refresh_token_expire_days == 1


# 서명 알고리즘은 문자열 비밀키를 쓰는 HMAC-SHA2 세 가지만 받는다. 비대칭 알고리즘(RS256, ES256), 서명 없음
# (none), 대소문자가 다른 이름(PyJWT도 모르는 이름이다), 빈 값은 거부한다.
@pytest.mark.parametrize("algorithm", ["RS256", "ES256", "none", "hs256", ""])
def test_signing_algorithms_other_than_hmac_sha2_are_refused(algorithm):
    with pytest.raises(ValidationError) as excinfo:
        make_settings(jwt_algorithm=algorithm)

    assert_rejected(excinfo, "jwt_algorithm", "literal_error")


# 허용한 세 알고리즘은 받고, 실제로 문자열 비밀키로 서명한 토큰이 같은 키·알고리즘으로 풀린다(그래서 이
# 셋만 허용한다).
@pytest.mark.parametrize("algorithm", ["HS256", "HS384", "HS512"])
def test_the_hmac_sha2_algorithms_are_accepted_and_sign_with_a_string_key(algorithm):
    settings = make_settings(jwt_algorithm=algorithm)

    token = jwt.encode({"sub": "user"}, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    claims = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])

    assert settings.jwt_algorithm == algorithm
    assert claims == {"sub": "user"}


# .env·환경 변수로 들어온 문자열도 같은 규칙으로 거부된다(실제 배포 경로).
@pytest.mark.parametrize(
    ("variable", "value", "field", "error_type"),
    [
        ("MODEL_THREADS", "0", "model_threads", "greater_than_equal"),
        ("ACCESS_TOKEN_EXPIRE_MINUTES", "-1", "access_token_expire_minutes", "greater_than_equal"),
        ("REFRESH_TOKEN_EXPIRE_DAYS", "0", "refresh_token_expire_days", "greater_than_equal"),
        ("JWT_ALGORITHM", "RS256", "jwt_algorithm", "literal_error"),
    ],
)
def test_out_of_range_environment_values_are_refused(monkeypatch, variable, value, field, error_type):
    monkeypatch.setenv(variable, value)

    with pytest.raises(ValidationError) as excinfo:
        make_settings()

    assert_rejected(excinfo, field, error_type)

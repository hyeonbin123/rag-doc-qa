"""Docker 이미지가 굽는 모델과 앱이 부르는 모델이 같은지, 실행 사용자가 root가 아닌지.

Dockerfile과 uv.lock을 글자로 읽어 비교한다. 이미지를 빌드하거나 모델을 받지는 않는다.
"""

# [테스트 묶음] Dockerfile의 정적 검사. 빌드 결과(층 크기, 컨테이너 안 오프라인 로딩)는 docker compose build로
# 따로 확인하고, 여기서는 빌드 전에 잡을 수 있는 어긋남만 본다.
# [왜 중요한가] 컨테이너는 HF_HUB_OFFLINE=1로 돌고, 이미지는 모델을 커밋 해시(리비전)로 받아 refs/main을
# 만들지 않는다. 그래서 Dockerfile이 받는 리비전과 앱 코드(app/services/embedding.py의 EMBEDDING_MODELS,
# app/services/reranking.py의 RERANKER_REVISIONS)가 부르는 리비전이 하나라도 다르면, 컨테이너가 시작할 때 그
# 모델을 캐시에서 찾지 못한다. 한쪽만 고치는 실수를 빌드하기 전에 잡는다.
# [import] tomllib은 uv.lock(TOML)을 읽는 표준 라이브러리다.

import re
import tomllib
from pathlib import Path

# 코드의 기본 모델 이름(Settings 필드 기본값)과 두 리비전 표를 가져온다.
from app.config import Settings
from app.services.embedding import EMBEDDING_MODELS
from app.services.reranking import RERANKER_REVISIONS

ROOT = Path(__file__).resolve().parents[1]
DOCKERFILE = (ROOT / "Dockerfile").read_text(encoding="utf-8")

# 모델 하나를 받는 명령 `$HF_CLI download <저장소> --revision <40자 커밋>`(HF_CLI는 hf CLI를 부르는 ARG).
# 뒤따르는 파일 목록은 보지 않는다.
DOWNLOAD = re.compile(r"\bdownload (\S+) --revision (\S+)")

# 이미지에 넣는 모델: 앱의 기본 모델 네 개(영어·한국어 임베딩, 영어·한국어 cross-encoder)와, 설정만 바꿔 v13
# 단계 B 전으로 되돌릴 수 있게 남겨 둔 한국어 임베딩 e5-small(README '2. 전체 스택 실행').
DEFAULT_MODEL_FIELDS = (
    "embedding_model_name",
    "embedding_model_name_ko",
    "reranker_model_name",
    "reranker_model_name_ko",
)
ROLLBACK_MODELS = ("intfloat/multilingual-e5-small",)


# 앱이 그 모델을 부를 때 쓰는 리비전. 임베딩 모델은 EMBEDDING_MODELS, cross-encoder는 RERANKER_REVISIONS에서
# 찾는다.
def runtime_revision(model_name: str) -> str | None:
    if model_name in EMBEDDING_MODELS:
        return EMBEDDING_MODELS[model_name].revision
    return RERANKER_REVISIONS.get(model_name)


# Dockerfile이 받는 모델 다섯 개가 정확히 위 목록이고, 각 리비전이 40자 커밋 해시이며 앱이 부르는 값과 같은지
# 본다. 모델이 빠지거나(컨테이너에서 못 찾음) 더 들어가거나(이미지만 커짐) 리비전이 어긋나면 실패한다.
def test_the_image_bakes_each_model_at_the_revision_the_app_loads():
    baked = dict(DOWNLOAD.findall(DOCKERFILE))
    expected_models = {Settings.model_fields[f].default for f in DEFAULT_MODEL_FIELDS}
    expected_models.update(ROLLBACK_MODELS)

    assert set(baked) == expected_models
    for model_name, revision in baked.items():
        assert re.fullmatch(r"[0-9a-f]{40}", revision), model_name
        assert revision == runtime_revision(model_name), model_name


# 모델을 받는 huggingface_hub와 hf-xet이 uv.lock의 판과 같은지 본다. 내려받는 쪽과 런타임(같은 lock으로
# 설치)이 같은 판이어야 캐시 형식이 어긋날 일이 없다. 모델 층은 lock 층보다 앞에 있어 lock을 읽지
# 못하므로(그래야 lock만 바꾼 재빌드가 모델을 다시 받지 않는다) 판을 Dockerfile에 직접 적고, 이 테스트가 둘을
# 맞춘다.
def test_the_model_downloader_is_the_locked_huggingface_hub():
    lock = tomllib.loads((ROOT / "uv.lock").read_text(encoding="utf-8"))
    locked = {package["name"]: package["version"] for package in lock["package"]}

    for package in ("huggingface-hub", "hf-xet"):
        assert f"{package}=={locked[package]}" in DOCKERFILE, package


# 마지막 USER 지시가 비루트 사용자 app(uid 10001)인지 본다. 그 뒤로 USER가 없으면 CMD(uvicorn)와
# `docker compose exec`가 이 사용자로 돈다.
def test_the_container_runs_as_an_unprivileged_user():
    users = re.findall(r"^USER\s+(\S+)", DOCKERFILE, flags=re.MULTILINE)

    assert users and users[-1] == "app"
    assert re.search(r"useradd\b[^\n]*--uid 10001\b[^\n]*\bapp\b", DOCKERFILE)

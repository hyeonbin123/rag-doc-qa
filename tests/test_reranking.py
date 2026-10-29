"""Cross-encoder 재정렬 모델을 어떻게 올리는지: 고정 리비전과 입력 최대 길이.

여기서는 실제 모델을 올리지 않는다. CrossEncoder를 생성자 인자만 기록하는 대역으로 바꾼다.
"""

# [테스트 묶음] app/services/reranking.py의 RerankerService가 cross-encoder를 어떤 인자로 올리는지 보는 단위
# 테스트. 실제 모델 파일은 받지 않는다.
# [왜 중요한가] Docker 이미지는 두 cross-encoder를 커밋 해시(리비전)로 받아 두고 refs/main을 만들지 않는다
# (Dockerfile). 그래서 런타임이 리비전 없이 부르면 HF_HUB_OFFLINE=1인 컨테이너에서는 캐시를 찾지 못해 rerank
# 모드가 시작하지 못하고, 호스트에서는 그날 허브의 main을 받아 측정 때와 다른 가중치가 들어올 수 있다. 그래서
# 기본 두 모델이 측정에 쓴 스냅숏의 리비전으로 올라가는지, 표에 없는 모델은 경고를 남기는지 고정한다.

import logging

import pytest

# 설정 클래스(코드의 기본 모델 이름), 재정렬 모듈과 그 리비전 표·최대 길이·서비스를 가져온다.
from app.config import Settings
from app.services import reranking
from app.services.reranking import MAX_LENGTH, RERANKER_REVISIONS, RerankerService

# 기본 두 모델: 영어 질문용 ms-marco(v6부터), 한국어 질문용 다국어 mmarco(v9부터).
MS_MARCO = "cross-encoder/ms-marco-MiniLM-L-6-v2"
MMARCO = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"


# CrossEncoder 대신 넣는 기록용 가짜. 생성자 인자를 클래스 목록에 남기기만 하고 모델은 받지 않는다.
class RecordingCrossEncoder:
    """생성자 인자를 기록만 하는 CrossEncoder 대역."""

    calls: list[tuple[str, dict]] = []

    def __init__(self, name: str, **kwargs) -> None:
        RecordingCrossEncoder.calls.append((name, kwargs))


# 테스트마다 기록 목록을 비우고 reranking 모듈의 CrossEncoder를 기록용 가짜로 바꾼다. 돌려받은 목록으로 생성자
# 인자를 확인한다.
@pytest.fixture
def recorded(monkeypatch):
    RecordingCrossEncoder.calls = []
    monkeypatch.setattr(reranking, "CrossEncoder", RecordingCrossEncoder)
    return RecordingCrossEncoder.calls


# 코드의 기본 두 모델이 리비전 표에 있고, 그 값(2026-10-30에 허브의 main이자 이미지와 로컬 캐시에 있던 유일한
# 스냅숏, 곧 v6·v9 측정부터 써 온 스냅숏)으로 올라가는지 확인한다. 최대 길이 512도 예전 그대로다. 기본값만
# 보려고 Settings의 필드 기본값을 읽는다(.env와 환경 변수는 보지 않음).
def test_the_default_cross_encoders_load_their_pinned_snapshots(recorded):
    assert Settings.model_fields["reranker_model_name"].default == MS_MARCO
    assert Settings.model_fields["reranker_model_name_ko"].default == MMARCO
    assert RERANKER_REVISIONS[MS_MARCO] == "233902d25c440f23af6f7d6e94d2946bac0bee0a"
    assert RERANKER_REVISIONS[MMARCO] == "1427fd652930e4ba29e8149678df786c240d8825"

    for model_name in (MS_MARCO, MMARCO):
        RerankerService(model_name)

        name, kwargs = recorded[-1]
        assert name == model_name
        assert kwargs == {"max_length": MAX_LENGTH, "revision": RERANKER_REVISIONS[model_name]}


# 표에 없는 모델(RERANKER_MODEL_NAME으로 다른 cross-encoder를 시험할 때)은 막지 않고 리비전 없이(허브 기본
# 브랜치) 올리되, 고정되지 않았다는 경고를 모델 이름과 함께 남긴다. 이미지 안에서는 그런 모델이 캐시에 없어
# 오프라인으로 올라가지 않으므로, 경고가 원인을 알려 준다.
def test_an_unknown_cross_encoder_loads_unpinned_with_a_warning(recorded, caplog):
    with caplog.at_level(logging.WARNING, logger="app.services.reranking"):
        RerankerService("some/other-cross-encoder")

    name, kwargs = recorded[-1]
    assert name == "some/other-cross-encoder"
    assert kwargs["revision"] is None
    assert [r.levelno for r in caplog.records if r.name == "app.services.reranking"] == [logging.WARNING]
    assert "some/other-cross-encoder" in caplog.text

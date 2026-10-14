"""임베딩 모델 설정: 접두사, 고정 리비전, Matryoshka 자르기, float32.

여기서는 실제 모델을 올리지 않는다. SentenceTransformer를 어떻게 생성됐는지만 기록하는 대역으로 바꾼다.
"""

# [테스트 묶음] 임베딩 모델 설정 표(app/services/embedding.py의 EMBEDDING_MODELS)와 EmbeddingService가 모델을
# 올리는 방식의 단위 테스트. 실제 모델 파일은 받지 않는다.
# [왜 중요한가] 접두사나 리비전, 자르기 차원, dtype이 하나라도 측정 때와 다르면 저장된 벡터와 질문 벡터가 다른
# 조건에서 만들어져, 오류 없이 검색 품질만 떨어진다. 그래서 v12에서 측정한 설정(리비전 고정, Matryoshka
# 자르기, float32)과 기존 모델의 해시 호환을 테스트로 고정한다(docs/experiments.md v12, v13 단계 B).
# [import] torch는 모델 인자로 넘어간 dtype이 torch.float32인지 비교하려고 가져온다.

import pytest
import torch

# 설정 기본값(한국어 모델), vector 열 크기, 임베딩 모듈의 표와 서비스, conftest의 가짜 임베딩을 가져온다.
from app.config import Settings
from app.models.chunk import EMBEDDING_DIM
from app.services import embedding
from app.services.embedding import EMBEDDING_MODELS, EmbeddingService, EmbeddingSpec, prefixes_for
from tests.conftest import FakeEmbeddingService

# 테스트에서 쓰는 모델 이름들: 영어 기본(bge), 이전 한국어 모델(e5-small), v12 후보 세 개(granite 97m·311m,
# Qwen3 0.6B).
E5_SMALL = "intfloat/multilingual-e5-small"
BGE_SMALL = "BAAI/bge-small-en-v1.5"
GRANITE_97M = "ibm-granite/granite-embedding-97m-multilingual-r2"
GRANITE_311M = "ibm-granite/granite-embedding-311m-multilingual-r2"
QWEN3_06B = "Qwen/Qwen3-Embedding-0.6B"


# SentenceTransformer 대신 넣는 기록용 가짜. 생성자 인자를 클래스 목록에 남기고, truncate_dim이 있으면 그
# 차원을, 없으면 native_dim(기본 384)을 출력 차원으로 보고한다. 모델을 받지 않고 '어떻게 올렸는가'만 검사할 수
# 있다.
class RecordingSentenceTransformer:
    """생성자 인자를 기록하고, 그 모델이 낼 출력 차원을 알려 준다."""

    native_dim = 384
    calls: list[tuple[str, dict]] = []

    def __init__(self, name: str, **kwargs) -> None:
        RecordingSentenceTransformer.calls.append((name, kwargs))
        self._dim = kwargs.get("truncate_dim") or self.native_dim

    def get_embedding_dimension(self) -> int:
        return self._dim


# 테스트마다 기록 목록을 비우고 embedding 모듈의 SentenceTransformer를 기록용 가짜로 바꾼다. 테스트는 돌려받은
# 목록으로 생성자 인자를 확인한다.
@pytest.fixture
def recorded(monkeypatch):
    RecordingSentenceTransformer.calls = []
    monkeypatch.setattr(embedding, "SentenceTransformer", RecordingSentenceTransformer)
    return RecordingSentenceTransformer.calls


# v12 후보 모델은 리비전이 40자 커밋 해시로 고정돼 있고, 접두사가 모델 카드대로인지 확인한다: Granite R2는
# 접두사 없음, Qwen3는 질문에만 'Instruct: ... Query:' 지시문.
def test_the_korean_candidates_have_pinned_revisions_and_their_prefixes():
    for name in (GRANITE_97M, GRANITE_311M, QWEN3_06B):
        revision = EMBEDDING_MODELS[name].revision
        assert revision is not None and len(revision) == 40
    # Granite R2는 접두사를 쓰지 않고, Qwen3는 질문 쪽에만 지시문을 붙인다.
    assert prefixes_for(GRANITE_97M) == ("", "")
    assert prefixes_for(GRANITE_311M) == ("", "")
    query_prefix, passage_prefix = prefixes_for(QWEN3_06B)
    assert query_prefix.startswith("Instruct: ") and query_prefix.endswith("\nQuery:")
    assert passage_prefix == ""


# 384차원보다 넓은 모델(311m 768차원, Qwen3 1024차원)은 vector(384) 열에 맞게 앞쪽 384개만 쓰도록 자르고, 원래
# 384인 97m은 자르지 않는다.
def test_wider_models_are_cut_to_the_vector_column_size():
    assert EMBEDDING_MODELS[GRANITE_97M].truncate_dim is None  # 원래 384차원
    assert EMBEDDING_MODELS[GRANITE_311M].truncate_dim == EMBEDDING_DIM
    assert EMBEDDING_MODELS[QWEN3_06B].truncate_dim == EMBEDDING_DIM


# 모델을 float32로, 고정 리비전과 자르기 차원을 넣어 올리는지 확인한다. transformers 5는 체크포인트에 적힌
# dtype으로 올리므로 Granite R2가 CPU에서 bfloat16이 되는 것을 확인했다(docs/experiments.md v12 dtype).
def test_models_load_in_float32_with_their_revision_and_truncation(recorded):
    EmbeddingService(GRANITE_311M)

    name, kwargs = recorded[-1]
    assert name == GRANITE_311M
    # transformers 5는 따로 지정하지 않으면 Granite R2 체크포인트를 bfloat16으로 올린다.
    assert kwargs["model_kwargs"] == {"dtype": torch.float32}
    assert kwargs["revision"] == EMBEDDING_MODELS[GRANITE_311M].revision
    assert kwargs["truncate_dim"] == EMBEDDING_DIM


# v8부터 쓰던 e5-small은 리비전·자르기 없이 예전과 똑같이 올라가야 한다(float32 명시는 원래 float32라 바뀌는
# 것이 없음). 바뀌면 이미 저장된 벡터와 어긋난다.
def test_the_models_already_in_use_load_as_before(recorded):
    EmbeddingService(E5_SMALL)

    name, kwargs = recorded[-1]
    assert name == E5_SMALL
    assert kwargs["revision"] is None
    assert kwargs["truncate_dim"] is None
    assert kwargs["model_kwargs"] == {"dtype": torch.float32}  # 이 모델들의 체크포인트는 float32다


# 자르기 설정 없이 1024차원을 내는 모델이면 서비스를 만들 때 바로 ValueError가 나야 한다. 그대로 두면 적재할
# 때 DB 오류나 잘못된 벡터로 늦게 드러난다. monkeypatch.setitem으로 표에 임시 모델을 넣고 테스트 뒤 되돌린다.
def test_a_model_whose_vectors_do_not_fit_the_column_fails_loudly(recorded, monkeypatch):
    class WideModel(RecordingSentenceTransformer):
        native_dim = 1024

    monkeypatch.setattr(embedding, "SentenceTransformer", WideModel)
    monkeypatch.setitem(EMBEDDING_MODELS, "some/wide-model", EmbeddingSpec("", ""))

    with pytest.raises(ValueError, match="1024"):
        EmbeddingService("some/wide-model")


# 적재 해시에 들어가는 identity가 e5·bge(그리고 가짜)에서는 모델 이름 그대로인지 확인한다. 리비전 등이 붙으면
# 해시가 바뀌어 저장된 모든 문서가 '바뀜'으로 보여 쓸데없이 다시 임베딩된다.
def test_identity_stays_the_bare_name_for_the_models_already_ingested(recorded):
    assert EmbeddingService(E5_SMALL).identity == E5_SMALL
    assert EmbeddingService(BGE_SMALL).identity == BGE_SMALL
    assert FakeEmbeddingService().identity == "fake-embedding"


# 새 모델의 identity에는 리비전(@...)과 자르기 차원(:dim384)이 들어가, 둘 중 하나만 바뀌어도 해시가 달라져
# 다시 적재된다.
def test_identity_names_the_revision_and_the_cut(recorded):
    spec = EMBEDDING_MODELS[GRANITE_311M]
    identity = EmbeddingService(GRANITE_311M).identity

    assert identity == f"{GRANITE_311M}@{spec.revision}:dim{EMBEDDING_DIM}"
    assert EmbeddingService(GRANITE_97M).identity == f"{GRANITE_97M}@{EMBEDDING_MODELS[GRANITE_97M].revision}"


# 한국어 기본 모델이 v13 단계 B에서 채택한 granite-311m이고, 측정한 리비전과 384 자르기가 그대로인지 고정한다.
# 환경 변수와 .env를 읽지 않게 해 코드의 기본값만 본다.
def test_the_korean_default_is_the_v13_stage_b_adoption(monkeypatch):
    # 한국어 모델은 granite-311m@384가 e5-small을 대신했다(docs/experiments.md v13 단계 B).
    monkeypatch.delenv("EMBEDDING_MODEL_NAME_KO", raising=False)
    settings = Settings(database_url="x", jwt_secret_key="y", _env_file=None)

    assert settings.embedding_model_name_ko == GRANITE_311M
    # 측정한 리비전과 자르기 차원, 그리고 예전과 같은 벡터 열 크기.
    assert EMBEDDING_MODELS[GRANITE_311M].revision == "44399559930365213510b1ee2eb15ded83374f0e"
    assert EMBEDDING_MODELS[GRANITE_311M].truncate_dim == EMBEDDING_DIM == 384

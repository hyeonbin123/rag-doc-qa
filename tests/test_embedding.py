"""Embedding model specs: prefixes, pinned revisions, Matryoshka truncation and float32.

The real models are not loaded here; SentenceTransformer is replaced with a stand-in that
records how it was constructed.
"""

import pytest
import torch

from app.models.chunk import EMBEDDING_DIM
from app.services import embedding
from app.services.embedding import EMBEDDING_MODELS, EmbeddingService, EmbeddingSpec, prefixes_for
from tests.conftest import FakeEmbeddingService

E5_SMALL = "intfloat/multilingual-e5-small"
BGE_SMALL = "BAAI/bge-small-en-v1.5"
GRANITE_97M = "ibm-granite/granite-embedding-97m-multilingual-r2"
GRANITE_311M = "ibm-granite/granite-embedding-311m-multilingual-r2"
QWEN3_06B = "Qwen/Qwen3-Embedding-0.6B"


class RecordingSentenceTransformer:
    """Records the constructor arguments; reports the dimension the model would output."""

    native_dim = 384
    calls: list[tuple[str, dict]] = []

    def __init__(self, name: str, **kwargs) -> None:
        RecordingSentenceTransformer.calls.append((name, kwargs))
        self._dim = kwargs.get("truncate_dim") or self.native_dim

    def get_embedding_dimension(self) -> int:
        return self._dim


@pytest.fixture
def recorded(monkeypatch):
    RecordingSentenceTransformer.calls = []
    monkeypatch.setattr(embedding, "SentenceTransformer", RecordingSentenceTransformer)
    return RecordingSentenceTransformer.calls


def test_the_korean_candidates_have_pinned_revisions_and_their_prefixes():
    for name in (GRANITE_97M, GRANITE_311M, QWEN3_06B):
        revision = EMBEDDING_MODELS[name].revision
        assert revision is not None and len(revision) == 40
    # Granite R2 takes no prefixes; Qwen3 instructs the query side only.
    assert prefixes_for(GRANITE_97M) == ("", "")
    assert prefixes_for(GRANITE_311M) == ("", "")
    query_prefix, passage_prefix = prefixes_for(QWEN3_06B)
    assert query_prefix.startswith("Instruct: ") and query_prefix.endswith("\nQuery:")
    assert passage_prefix == ""


def test_wider_models_are_cut_to_the_vector_column_size():
    assert EMBEDDING_MODELS[GRANITE_97M].truncate_dim is None  # already 384
    assert EMBEDDING_MODELS[GRANITE_311M].truncate_dim == EMBEDDING_DIM
    assert EMBEDDING_MODELS[QWEN3_06B].truncate_dim == EMBEDDING_DIM


def test_models_load_in_float32_with_their_revision_and_truncation(recorded):
    EmbeddingService(GRANITE_311M)

    name, kwargs = recorded[-1]
    assert name == GRANITE_311M
    # transformers 5 loads the Granite R2 checkpoints in bfloat16 unless told otherwise.
    assert kwargs["model_kwargs"] == {"dtype": torch.float32}
    assert kwargs["revision"] == EMBEDDING_MODELS[GRANITE_311M].revision
    assert kwargs["truncate_dim"] == EMBEDDING_DIM


def test_the_models_already_in_use_load_as_before(recorded):
    EmbeddingService(E5_SMALL)

    name, kwargs = recorded[-1]
    assert name == E5_SMALL
    assert kwargs["revision"] is None
    assert kwargs["truncate_dim"] is None
    assert kwargs["model_kwargs"] == {"dtype": torch.float32}  # their checkpoints are float32


def test_a_model_whose_vectors_do_not_fit_the_column_fails_loudly(recorded, monkeypatch):
    class WideModel(RecordingSentenceTransformer):
        native_dim = 1024

    monkeypatch.setattr(embedding, "SentenceTransformer", WideModel)
    monkeypatch.setitem(EMBEDDING_MODELS, "some/wide-model", EmbeddingSpec("", ""))

    with pytest.raises(ValueError, match="1024"):
        EmbeddingService("some/wide-model")


def test_identity_stays_the_bare_name_for_the_models_already_ingested(recorded):
    # Ingestion hashes the identity. For e5 and bge it must stay the model name, or every
    # stored document would look changed and be re-embedded for nothing.
    assert EmbeddingService(E5_SMALL).identity == E5_SMALL
    assert EmbeddingService(BGE_SMALL).identity == BGE_SMALL
    assert FakeEmbeddingService().identity == "fake-embedding"


def test_identity_names_the_revision_and_the_cut(recorded):
    spec = EMBEDDING_MODELS[GRANITE_311M]
    identity = EmbeddingService(GRANITE_311M).identity

    assert identity == f"{GRANITE_311M}@{spec.revision}:dim{EMBEDDING_DIM}"
    assert EmbeddingService(GRANITE_97M).identity == f"{GRANITE_97M}@{EMBEDDING_MODELS[GRANITE_97M].revision}"

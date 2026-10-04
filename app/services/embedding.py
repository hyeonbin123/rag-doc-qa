"""Wraps the local sentence-transformers model.

Retrieval embedding models are asymmetric: queries and passages get different
markers (an instruction prefix for BGE and Qwen3, "query: " / "passage: " for E5). Getting
this backwards silently degrades retrieval quality, so the two embedding paths are
kept as separate methods rather than one generic `embed()` to make the asymmetry
impossible to miss at call sites.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

import torch
from sentence_transformers import SentenceTransformer

from app.config import get_settings
from app.models.chunk import EMBEDDING_DIM
from app.services.language import Language


@dataclass(frozen=True)
class EmbeddingSpec:
    query_prefix: str
    passage_prefix: str
    # Hub commit to load. The models added for the v12 comparison are pinned; the two in
    # use since v8 were never pinned and stay that way, so their stored vectors still match.
    revision: str | None = None
    # Matryoshka models trained to be cut: keep the first `truncate_dim` components so the
    # vectors fit the vector(384) column.
    truncate_dim: int | None = None


EMBEDDING_MODELS: dict[str, EmbeddingSpec] = {
    "BAAI/bge-small-en-v1.5": EmbeddingSpec(
        "Represent this sentence for searching relevant passages: ", ""
    ),
    "intfloat/multilingual-e5-small": EmbeddingSpec("query: ", "passage: "),
    # Korean candidates measured in docs/experiments.md v12. Granite R2 takes no prefixes;
    # Qwen3 instructs the query side with the prompt its model card ships as "query".
    "ibm-granite/granite-embedding-97m-multilingual-r2": EmbeddingSpec(
        "", "", revision="835ad14087e140460703cf0fae09f97d469d65c2"
    ),
    "ibm-granite/granite-embedding-311m-multilingual-r2": EmbeddingSpec(
        "", "", revision="44399559930365213510b1ee2eb15ded83374f0e", truncate_dim=EMBEDDING_DIM
    ),
    "Qwen/Qwen3-Embedding-0.6B": EmbeddingSpec(
        "Instruct: Given a web search query, retrieve relevant passages that answer the query\nQuery:",
        "",
        revision="97b0c614be4d77ee51c0cef4e5f07c00f9eb65b3",
        truncate_dim=EMBEDDING_DIM,
    ),
}


def spec_for(model_name: str) -> EmbeddingSpec:
    try:
        return EMBEDDING_MODELS[model_name]
    except KeyError:
        raise ValueError(
            f"No query/passage prefixes known for embedding model {model_name!r}; "
            "add it to EMBEDDING_MODELS"
        ) from None


def prefixes_for(model_name: str) -> tuple[str, str]:
    spec = spec_for(model_name)
    return spec.query_prefix, spec.passage_prefix


class EmbeddingService:
    # Class-level defaults, so test doubles that skip __init__ still have them.
    revision: str | None = None
    truncate_dim: int | None = None

    def __init__(self, model_name: str) -> None:
        spec = spec_for(model_name)
        self.model_name = model_name
        self.revision = spec.revision
        self.truncate_dim = spec.truncate_dim
        self._query_prefix, self._passage_prefix = spec.query_prefix, spec.passage_prefix
        # float32 explicitly: transformers 5 otherwise loads a checkpoint in the dtype it
        # was saved in, which for the Granite R2 models is bfloat16 (slow and less exact
        # on a CPU). The e5 and bge checkpoints are float32 already.
        self._model = SentenceTransformer(
            model_name,
            revision=spec.revision,
            truncate_dim=spec.truncate_dim,
            model_kwargs={"dtype": torch.float32},
        )
        dim = self._model.get_embedding_dimension()
        if dim != EMBEDDING_DIM:
            raise ValueError(
                f"{model_name} outputs {dim}-dimensional vectors but chunks.embedding is "
                f"vector({EMBEDDING_DIM}); set truncate_dim in its EmbeddingSpec"
            )

    @property
    def identity(self) -> str:
        """What ingestion hashes as "the model": a different revision or cut re-embeds.

        The bare model name for the models in use since v8, so documents ingested before
        this field existed keep their content hash.
        """
        identity = self.model_name
        if self.revision:
            identity += f"@{self.revision}"
        if self.truncate_dim:
            identity += f":dim{self.truncate_dim}"
        return identity

    def embed_query(self, text: str) -> list[float]:
        vector = self._model.encode(self._query_prefix + text, normalize_embeddings=True)
        return vector.tolist()

    def embed_passages(self, texts: list[str]) -> list[list[float]]:
        vectors = self._model.encode(
            [self._passage_prefix + t for t in texts], normalize_embeddings=True
        )
        return vectors.tolist()


@lru_cache
def _load(model_name: str) -> EmbeddingService:
    return EmbeddingService(model_name)


def get_embedding_service(language: Language = "en") -> EmbeddingService:
    """The embedding model for one docs language.

    Each language's chunks are embedded with that language's model (see
    Settings.embedding_model_for), so a question has to be embedded with the same one.
    """
    return _load(get_settings().embedding_model_for(language))

"""Wraps the local sentence-transformers model.

Retrieval embedding models are asymmetric: queries and passages get different
markers (an instruction prefix for BGE, "query: " / "passage: " for E5). Getting
this backwards silently degrades retrieval quality, so the two embedding paths are
kept as separate methods rather than one generic `embed()` to make the asymmetry
impossible to miss at call sites.
"""

from __future__ import annotations

from functools import lru_cache

from sentence_transformers import SentenceTransformer

from app.config import get_settings
from app.services.language import Language

# (query prefix, passage prefix) for each supported model.
PREFIXES: dict[str, tuple[str, str]] = {
    "BAAI/bge-small-en-v1.5": ("Represent this sentence for searching relevant passages: ", ""),
    "intfloat/multilingual-e5-small": ("query: ", "passage: "),
}


def prefixes_for(model_name: str) -> tuple[str, str]:
    try:
        return PREFIXES[model_name]
    except KeyError:
        raise ValueError(
            f"No query/passage prefixes known for embedding model {model_name!r}; "
            "add them to PREFIXES"
        ) from None


class EmbeddingService:
    def __init__(self, model_name: str) -> None:
        self.model_name = model_name
        self._query_prefix, self._passage_prefix = prefixes_for(model_name)
        self._model = SentenceTransformer(model_name)

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

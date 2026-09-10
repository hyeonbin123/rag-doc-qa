"""Wraps the local sentence-transformers model.

BGE models use an asymmetric convention: queries get an instruction prefix,
passages do not. Getting this backwards silently degrades retrieval quality,
so the two embedding paths are kept as separate methods rather than one
generic `embed()` to make the asymmetry impossible to miss at call sites.
"""

from __future__ import annotations

from functools import lru_cache

from sentence_transformers import SentenceTransformer

from app.config import get_settings

QUERY_INSTRUCTION = "Represent this sentence for searching relevant passages: "


class EmbeddingService:
    def __init__(self, model_name: str) -> None:
        self._model = SentenceTransformer(model_name)

    def embed_query(self, text: str) -> list[float]:
        vector = self._model.encode(QUERY_INSTRUCTION + text, normalize_embeddings=True)
        return vector.tolist()

    def embed_passages(self, texts: list[str]) -> list[list[float]]:
        vectors = self._model.encode(texts, normalize_embeddings=True)
        return vectors.tolist()


@lru_cache
def get_embedding_service() -> EmbeddingService:
    settings = get_settings()
    return EmbeddingService(settings.embedding_model_name)

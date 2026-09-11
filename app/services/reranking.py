"""Cross-encoder reranking.

The embedding model is a bi-encoder: the question and each passage are embedded
separately, which is what lets passages be embedded and indexed ahead of time. A
cross-encoder reads the question and a passage together, so it judges relevance more
precisely, but it has to run once per (question, passage) pair at query time. That is
why it only reorders a short candidate list instead of searching the whole corpus.
"""

from __future__ import annotations

from functools import lru_cache

import torch
from sentence_transformers import CrossEncoder

from app.config import get_settings

MAX_LENGTH = 512
BATCH_SIZE = 16


class RerankerService:
    def __init__(self, model_name: str) -> None:
        self._model = CrossEncoder(model_name, max_length=MAX_LENGTH)

    def score(self, question: str, passages: list[str]) -> list[float]:
        """Relevance of each passage to the question, as a probability in (0, 1).

        MS MARCO cross-encoders return raw logits while BGE rerankers apply a sigmoid
        by default; forcing the sigmoid gives every model the same score scale.
        """
        if not passages:
            return []
        scores = self._model.predict(
            [(question, p) for p in passages],
            batch_size=BATCH_SIZE,
            activation_fn=torch.nn.Sigmoid(),
        )
        return [float(s) for s in scores]


@lru_cache
def get_reranker_service() -> RerankerService:
    return RerankerService(get_settings().reranker_model_name)

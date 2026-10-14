"""Cross-encoder 재정렬.

임베딩 모델은 bi-encoder다: 질문과 각 문서 조각(passage)을 따로 임베딩하므로, 문서 조각을 미리 임베딩해
인덱스에 넣어 둘 수 있다. cross-encoder는 질문과 문서 조각을 함께 읽어 관련도를 더 정확히 판단하지만,
질의 시점에 (질문, 문서 조각) 쌍마다 한 번씩 돌려야 한다. 그래서 전체 코퍼스를 검색하는 대신 짧은 후보
목록의 순서만 다시 매긴다.
"""

# [파일 역할] RETRIEVAL_MODE=rerank에서 검색 후보를 cross-encoder로 다시 채점하는 서비스. 위 docstring처럼
# 질문과 본문을 함께 읽어 관련도를 더 정확히 보지만, 후보마다 모델을 한 번씩 돌려야 해서 짧은 후보 목록에만
# 쓴다.
# [배경] v6에서 영어 모델(ms-marco-MiniLM-L-6-v2)로 추가했고, v9에서 한국어 질문에는 다국어
# 모델(mmarco-mMiniLMv2-L12)을 쓰도록 언어별로 나눴다. 영어 전용 모델은 한국어 튜닝용 셋에서 재정렬을 안 한
# 것보다도 낮았다(docs/experiments.md v9). 기본 모드는 dense라 이 모듈은 설정으로 켰을 때만 쓰인다.
# [연결] app/services/retrieval.py의 rerank_search가 score를 모델 스레드(run_model)에서 부른다. 모델 선택은
# Settings.reranker_model_for.

from __future__ import annotations

from functools import lru_cache

# torch: 점수에 시그모이드를 씌울 활성화 함수(torch.nn.Sigmoid)를 넘기려고 가져온다. CrossEncoder:
# sentence-transformers의 cross-encoder 래퍼(질문·본문 쌍 → 점수).
import torch
from sentence_transformers import CrossEncoder

from app.config import get_settings
from app.services.language import Language

# MAX_LENGTH: 질문+본문 쌍을 자르는 최대 토큰 수(512, BERT 계열 모델의 일반적인 입력 한도). 긴 청크는 뒷부분이
# 잘린 채 채점된다. BATCH_SIZE: 한 번의 forward에 넣는 쌍 수.
MAX_LENGTH = 512
BATCH_SIZE = 16


# cross-encoder 모델 하나를 감싼다. 생성자에서 모델 파일을 올리므로 비싸다. 그래서 아래 _load가 모델 이름별로
# 한 번만 만든다.
class RerankerService:
    def __init__(self, model_name: str) -> None:
        self._model = CrossEncoder(model_name, max_length=MAX_LENGTH)

    def score(self, question: str, passages: list[str]) -> list[float]:
        """각 문서 조각이 질문과 얼마나 관련 있는지를 (0, 1) 사이 확률로 돌려준다.

        MS MARCO cross-encoder는 날것의 로짓을 돌려주고 BGE reranker는 기본으로 시그모이드를 씌운다.
        시그모이드를 늘 씌우게 강제하면 어느 모델이든 점수 척도가 같아진다.
        """
        # 후보가 없으면 모델을 부르지 않는다.
        if not passages:
            return []
        # (질문, 본문) 쌍을 배치로 채점한다. 시그모이드로 0~1 확률로 바꾸므로, rerank 모드의 score는 모델이
        # 바뀌어도 같은 척도가 된다. numpy 실수를 파이썬 float로 바꿔 JSON 직렬화(질문 기록)에 문제가 없게
        # 한다.
        scores = self._model.predict(
            [(question, p) for p in passages],
            batch_size=BATCH_SIZE,
            activation_fn=torch.nn.Sigmoid(),
        )
        return [float(s) for s in scores]


# 모델 이름 → 서비스 객체 캐시. 같은 모델을 여러 언어가 쓰더라도 한 번만 올린다.
@lru_cache
def _load(model_name: str) -> RerankerService:
    return RerankerService(model_name)


# 질문 언어에 맞는 cross-encoder를 돌려준다. 앱에서는 app/dependencies.py의 get_reranker가 이 함수를 '언어 →
# 모델' 조회 함수로 주입하고, app/main.py가 rerank 모드일 때 시작하면서 두 언어 모델을 미리 올린다. 평가
# 스크립트도 이 함수를 쓴다.
def get_reranker_service(language: Language = "en") -> RerankerService:
    """`language` 질문에 쓰는 cross-encoder. 모델마다 한 번만 올린다."""
    return _load(get_settings().reranker_model_for(language))

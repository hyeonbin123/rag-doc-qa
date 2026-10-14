"""로컬 sentence-transformers 모델을 감싼다.

검색용 임베딩 모델은 비대칭이다. 질문과 문서(passage)에 서로 다른 표시를 붙인다(BGE와 Qwen3는 질문에
지시문 접두사, E5는 "query: " / "passage: "). 이것을 뒤바꾸면 오류 없이 검색 품질만 조용히 떨어진다.
그래서 범용 `embed()` 하나 대신 두 임베딩 경로를 별도 메서드로 나눠, 호출하는 곳에서 이 비대칭을 놓칠
수 없게 했다.
"""

# [파일 역할] 로컬 sentence-transformers 임베딩 모델을 감싸, 질문 벡터(embed_query)와 문서 청크
# 벡터(embed_passages)를 만든다. 모델마다 다른 접두사·리비전·자르기 차원을 표(EMBEDDING_MODELS)로 관리한다.
# [설계 이유]
# - 위 docstring처럼 질문용·문서용 함수를 나눠 호출하는 쪽에서 접두사를 헷갈릴 수 없게 했다(README '로컬
#   모델').
# - 모델 이름으로 설정을 찾게 해, 표에 없는 모델은 시작할 때 바로 오류가 난다(잘못된 접두사로 조용히 품질이
#   떨어지는 것을 막음).
# - 영어와 한국어는 서로 다른 모델을 쓴다(영어 bge-small-en, 한국어는 v13 단계 B부터 Granite R2 311M을
#   384차원으로 자름). 모든 벡터는 chunks.embedding의 vector(384)에 들어가야 한다.
# [연결] 질문 임베딩(app/routers/query.py), 적재(app/services/ingestion.py, scripts/ingest_fastapi_docs.py),
# 평가 스크립트가 get_embedding_service로 언어별 모델을 받는다.

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

# torch: 모델을 float32로 올리도록 dtype을 지정하는 데 쓴다. SentenceTransformer: 허브 모델을 받아 문장 →
# 벡터로 바꾸는 래퍼(풀링·정규화 포함).
import torch
from sentence_transformers import SentenceTransformer

from app.config import get_settings
from app.models.chunk import EMBEDDING_DIM
from app.services.language import Language


# 모델 하나의 임베딩 규칙. 질문 앞에 붙일 접두사, 문서 앞에 붙일 접두사, 고정할 허브 리비전, 자를 차원.
# frozen이라 표의 값을 실수로 바꿀 수 없다.
@dataclass(frozen=True)
class EmbeddingSpec:
    query_prefix: str
    passage_prefix: str
    # 불러올 허브 커밋(리비전). v12 비교 때 더한 모델은 리비전을 고정했다. v8부터 쓰던 두 모델은 처음부터
    # 고정하지 않았고 지금도 그대로 둔다. 그래야 이미 저장된 벡터와 계속 맞는다.
    revision: str | None = None
    # 잘라 쓰도록 학습된 Matryoshka 모델: 앞쪽 `truncate_dim`개 성분만 남겨 vector(384) 열에 맞춘다.
    truncate_dim: int | None = None


# 모델 이름 → 규칙 표. 지금 기본으로 쓰는 것은 영어 bge-small-en-v1.5와 한국어 granite-embedding-311m이고,
# 나머지는 비교·되돌리기용이다.
# - bge-small-en-v1.5: 질문에만 검색용 지시문을 붙이고 문서에는 붙이지 않는다.
# - multilingual-e5-small: 'query: ' / 'passage: '를 붙인다(v8~v13 단계 B 전까지의 한국어 모델, 이미지에 남아
#   있음).
# - granite 97m / 311m: 접두사 없음. v12 비교 때 넣으며 리비전을 고정했다. 311m은 768차원이라 384로
#   자른다(Matryoshka 학습 모델, docs/experiments.md v12 후보 표).
# - Qwen3-Embedding-0.6B: 1024차원을 384로 자르고 질문에만 모델 카드의 지시문을 붙인다. v12에서 CPU 질의
#   임베딩이 315ms로 예산(100ms)을 넘어 탈락했다.
EMBEDDING_MODELS: dict[str, EmbeddingSpec] = {
    "BAAI/bge-small-en-v1.5": EmbeddingSpec(
        "Represent this sentence for searching relevant passages: ", ""
    ),
    "intfloat/multilingual-e5-small": EmbeddingSpec("query: ", "passage: "),
    # docs/experiments.md v12에서 잰 한국어 후보들. Granite R2는 접두사를 쓰지 않는다. Qwen3는 모델 카드가
    # "query" 프롬프트로 제공하는 지시문을 질문 쪽에만 붙인다.
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


# 표에서 모델 규칙을 찾는다. 없으면 KeyError 대신 무엇을 해야 하는지 알려 주는 ValueError를 낸다(from None으로
# 원래 KeyError 추적은 숨긴다).
def spec_for(model_name: str) -> EmbeddingSpec:
    try:
        return EMBEDDING_MODELS[model_name]
    except KeyError:
        raise ValueError(
            f"No query/passage prefixes known for embedding model {model_name!r}; "
            "add it to EMBEDDING_MODELS"
        ) from None


# (질문 접두사, 문서 접두사) 쌍만 돌려주는 도우미. 테스트(tests/test_embedding.py)가 모델별 접두사를 확인하는
# 데 쓴다.
def prefixes_for(model_name: str) -> tuple[str, str]:
    spec = spec_for(model_name)
    return spec.query_prefix, spec.passage_prefix


# 임베딩 모델 하나. 생성자가 모델을 올리므로 비싸고, 아래 _load가 모델 이름별로 한 번만 만든다. 테스트의 가짜
# 서비스(tests/conftest.py의 FakeEmbeddingService)는 이 클래스를 상속하되 생성자를 건너뛴다.
class EmbeddingService:
    # 클래스 수준 기본값. __init__을 건너뛰는 테스트 대역도 이 속성을 갖게 한다.
    revision: str | None = None
    truncate_dim: int | None = None

    def __init__(self, model_name: str) -> None:
        spec = spec_for(model_name)
        self.model_name = model_name
        self.revision = spec.revision
        self.truncate_dim = spec.truncate_dim
        self._query_prefix, self._passage_prefix = spec.query_prefix, spec.passage_prefix
        # float32를 명시한다: 그러지 않으면 transformers 5는 체크포인트를 저장된 dtype 그대로 올리는데,
        # Granite R2 모델은 bfloat16이라 CPU에서 느리고 덜 정확하다. e5와 bge 체크포인트는 이미 float32다.
        self._model = SentenceTransformer(
            model_name,
            revision=spec.revision,
            truncate_dim=spec.truncate_dim,
            model_kwargs={"dtype": torch.float32},
        )
        # 자르기를 적용한 뒤의 출력 차원이 DB 열(vector(384))과 다르면 올리는 시점에 바로 실패시킨다. 그대로
        # 두면 적재하거나 검색할 때 DB 오류로 늦게 드러난다.
        dim = self._model.get_embedding_dimension()
        if dim != EMBEDDING_DIM:
            raise ValueError(
                f"{model_name} outputs {dim}-dimensional vectors but chunks.embedding is "
                f"vector({EMBEDDING_DIM}); set truncate_dim in its EmbeddingSpec"
            )

    # 적재 해시(app/services/ingestion.py)와 평가 리포트에 기록하는 '모델 식별자'. 이름@리비전:dim자르기
    # 형태라, 같은 모델이라도 리비전이나 자르기가 바뀌면 해시가 달라져 문서가 다시 임베딩된다.
    @property
    def identity(self) -> str:
        """적재가 '모델'로 해시하는 값. 리비전이나 자르기 차원이 다르면 문서를 다시 임베딩한다.

        v8부터 쓰던 모델은 리비전·자르기가 없어 모델 이름만 돌려준다. 그래서 이 속성이 생기기 전에
        적재한 문서도 내용 해시가 그대로 유지된다.
        """
        identity = self.model_name
        if self.revision:
            identity += f"@{self.revision}"
        if self.truncate_dim:
            identity += f":dim{self.truncate_dim}"
        return identity

    # 질문 하나를 임베딩한다. normalize_embeddings=True로 길이 1인 벡터를 만들어, pgvector 코사인 거리로
    # 비교한 1 - 거리가 코사인 유사도가 되게 한다. pgvector 바인딩에 넘기기 쉽게 파이썬 리스트로 바꾼다. CPU를
    # 쓰는 동기 호출이라 호출하는 쪽이 run_model로 스레드에서 부른다.
    def embed_query(self, text: str) -> list[float]:
        vector = self._model.encode(self._query_prefix + text, normalize_embeddings=True)
        return vector.tolist()

    # 적재할 청크 여러 개를 한 번에(배치로) 임베딩한다. 문서용 접두사를 붙이고 질문과 같은 방식으로
    # 정규화한다.
    def embed_passages(self, texts: list[str]) -> list[list[float]]:
        vectors = self._model.encode(
            [self._passage_prefix + t for t in texts], normalize_embeddings=True
        )
        return vectors.tolist()


# 모델 이름 → 서비스 캐시. 두 언어가 같은 모델을 쓰도록 설정하더라도 모델은 한 번만 올라간다.
@lru_cache
def _load(model_name: str) -> EmbeddingService:
    return EmbeddingService(model_name)


# 언어 → 그 언어의 임베딩 서비스. app/dependencies.py의 get_embedder가 이 함수 자체를 주입하고, app/main.py가
# 시작할 때 두 언어 모델을 미리 올린다.
def get_embedding_service(language: Language = "en") -> EmbeddingService:
    """문서 언어 하나에 쓰는 임베딩 모델.

    각 언어의 청크는 그 언어의 모델로 임베딩되므로(Settings.embedding_model_for 참고), 질문도 반드시
    같은 모델로 임베딩해야 한다.
    """
    return _load(get_settings().embedding_model_for(language))

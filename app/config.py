from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    generation_provider: Literal["anthropic", "ollama"] = "ollama"
    anthropic_api_key: str = ""
    claude_model_name: str = "claude-sonnet-5"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model_name: str = "qwen2.5:7b-instruct"
    embedding_model_name: str = "BAAI/bge-small-en-v1.5"
    # Korean docs and questions need a multilingual model; English keeps the English
    # one because the multilingual model scored far lower on the English test sets.
    embedding_model_name_ko: str = "intfloat/multilingual-e5-small"
    retrieval_mode: Literal["dense", "hybrid", "rerank"] = "dense"
    reranker_model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    # The model above was trained on English only; on the Korean tuning set it ranked
    # worse than no reranking at all, so Korean questions get a multilingual one.
    reranker_model_name_ko: str = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"
    # Worker threads for CPU-bound model calls (embeddings, the cross-encoder). 6 was
    # measured against 1 on a 12-core desktop; see app/services/inference.py.
    model_threads: int = 6
    fastapi_docs_commit_sha: str = ""
    admin_ingest_token: str = "change-me-admin-token"

    def embedding_model_for(self, language: str) -> str:
        return self.embedding_model_name_ko if language == "ko" else self.embedding_model_name

    def reranker_model_for(self, language: str) -> str:
        return self.reranker_model_name_ko if language == "ko" else self.reranker_model_name


@lru_cache
def get_settings() -> Settings:
    return Settings()

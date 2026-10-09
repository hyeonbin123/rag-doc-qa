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
    # A.X-4.0-Light (Q4_K_M), built locally with scripts/ax40_light/; adopted in v13 over
    # qwen2.5:7b-instruct, which stays the judge (docs/experiments.md v13).
    ollama_model_name: str = "a.x-4.0-light:q4_k_m"
    # Sent as Ollama's `think` field when set; models that reason by default (qwen3.5)
    # need false. Unset sends no field, as before v13 (docs/experiments.md).
    ollama_think: bool | None = None
    # Regenerate once a Korean answer that slipped into Chinese or Japanese (v13; on since
    # the v13 adoption).
    language_guard: bool = True
    embedding_model_name: str = "BAAI/bge-small-en-v1.5"
    # Korean docs and questions need a multilingual model; English keeps the English
    # one because the multilingual model scored far lower on the English test sets.
    # Granite R2 311M cut to 384 dimensions, adopted in v13 stage B over
    # intfloat/multilingual-e5-small, which stays in the image (docs/experiments.md).
    embedding_model_name_ko: str = "ibm-granite/granite-embedding-311m-multilingual-r2"
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

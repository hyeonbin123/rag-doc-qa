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
    fastapi_docs_commit_sha: str = ""
    admin_ingest_token: str = "change-me-admin-token"


@lru_cache
def get_settings() -> Settings:
    return Settings()

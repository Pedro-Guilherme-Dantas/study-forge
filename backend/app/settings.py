from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=None, extra="ignore")

    app_mode: Literal["fixture", "real"] = "fixture"
    database_url: str = (
        "postgresql+psycopg://studyforge:studyforge-local@db:5432/studyforge"
    )
    gemini_api_key: SecretStr = SecretStr("")
    search_api_key: SecretStr = SecretStr("")
    gemini_backend: Literal["developer", "vertex"] = "developer"
    gemini_project: str = ""
    gemini_location: str = ""
    gemini_generation_model: str = "gemini-3.5-flash-lite"
    gemini_embedding_model: str = "gemini-embedding-001"
    langsmith_tracing: bool = False
    langchain_tracing_v2: bool = False
    log_payloads: bool = False
    max_upload_bytes: int = Field(1_048_576, ge=1)
    max_html_bytes: int = Field(2_097_152, ge=1)
    max_pages_per_research: int = Field(5, ge=1, le=20)
    max_temporary_sources: int = Field(20, ge=1, le=100)
    max_message_bytes: int = Field(131_072, ge=1)
    max_temporary_bytes: int = Field(8_388_608, ge=1)
    max_graph_steps: int = Field(8, ge=1, le=64)
    max_external_attempts: int = Field(20, ge=1, le=100)
    max_ingestions: int = Field(1, ge=1, le=2)
    max_queued_ingestions: int = Field(5, ge=1, le=20)
    embedding_dimensions: Literal[768] = 768
    embedding_batch_size: int = Field(32, ge=1, le=100)
    retrieval_top_k: int = Field(5, ge=1, le=20)
    chunk_target: int = Field(1600, ge=64)
    chunk_max: int = Field(2400, ge=64)
    chunk_overlap: int = Field(200, ge=0)
    turn_timeout: float = Field(60.0, gt=0)
    ingestion_timeout: float = Field(120.0, gt=0)

    @model_validator(mode="after")
    def validate_policy(self):
        if self.langsmith_tracing or self.langchain_tracing_v2 or self.log_payloads:
            raise ValueError("Payload tracing is not supported in this application")
        if not 0 <= self.chunk_overlap < self.chunk_target <= self.chunk_max:
            raise ValueError("Invalid textual chunk configuration")
        return self

    @property
    def embedding_profile(self) -> str:
        if self.app_mode == "fixture":
            return "fixture-hash-v1:768"
        return f"gemini:{self.gemini_embedding_model}:768:l2:retrieval-v1"

    def public_limits(self) -> dict[str, int]:
        return {
            name: getattr(self, name)
            for name in (
                "max_upload_bytes",
                "max_html_bytes",
                "max_pages_per_research",
                "max_temporary_sources",
                "max_message_bytes",
                "max_graph_steps",
                "max_external_attempts",
                "embedding_dimensions",
                "retrieval_top_k",
            )
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()

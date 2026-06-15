from __future__ import annotations

from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "IncidentIQ"
    app_version: str = "1.0.0"
    app_env: str = "development"
    debug: bool = False
    app_secret_key: str = "change-me-in-production"

    # MongoDB
    mongodb_uri: str
    mongodb_database: str = "incidentiq"

    # Groq
    groq_api_key: str
    groq_model: str = "llama-3.3-70b-versatile"
    groq_max_tokens: int = 2048
    groq_temperature: float = 0.1

    # Embeddings
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    vector_dimensions: int = 384
    vector_index_name: str = "incidentiq_vector_index"

    # File Storage
    upload_dir: str = "/tmp/incidentiq/uploads"
    max_file_size_mb: int = 50

    # CORS
    allowed_origins: list[str] = ["http://localhost:3000"]

    # Ingestion Pipeline
    chunk_size: int = 512
    chunk_overlap: int = 50
    max_chunks_per_document: int = 500
    similarity_search_limit: int = 10

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_origins(cls, v: str | list) -> list[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    return Settings()

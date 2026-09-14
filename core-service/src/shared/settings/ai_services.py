from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class EmbeddingServiceSettings(BaseSettings):
    URL: str = ...
    BATCH_SIZE: int = Field(default=10, gt=0)

    model_config = SettingsConfigDict(
        env_file=Path(".env"),
        extra="forbid",
        dotenv_filtering="match_prefix",
        case_sensitive=True,
        frozen=True,
        env_prefix="EMBEDDING_SERVICE_",
    )


class ExtractionServiceSettings(BaseSettings):
    URL: str = ...

    model_config = SettingsConfigDict(
        env_file=Path(".env"),
        extra="forbid",
        dotenv_filtering="match_prefix",
        case_sensitive=True,
        frozen=True,
        env_prefix="EXTRACTION_SERVICE_",
    )


embedding_service_settings = EmbeddingServiceSettings()
extraction_service_settings = ExtractionServiceSettings()

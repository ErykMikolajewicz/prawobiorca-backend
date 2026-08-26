from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class EmbeddingServiceSettings(BaseSettings):
    URL: str = ...

    model_config = SettingsConfigDict(
        env_file=Path(".env"), extra="ignore", case_sensitive=True, frozen=True, env_prefix="EMBEDDING_SERVICE_"
    )


class ExtractionServiceSettings(BaseSettings):
    URL: str = ...

    model_config = SettingsConfigDict(
        env_file=Path(".env"), extra="ignore", case_sensitive=True, frozen=True, env_prefix="EXTRACTION_SERVICE_"
    )


embedding_service_settings = EmbeddingServiceSettings()
extraction_service_settings = ExtractionServiceSettings()

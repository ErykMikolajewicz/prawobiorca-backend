from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class EmbeddingsSettings(BaseSettings):
    URL: str = ...

    model_config = SettingsConfigDict(
        env_file=Path(".env"), extra="ignore", case_sensitive=True, frozen=True, env_prefix="EMBEDDING_"
    )


embeddings_settings = EmbeddingsSettings()
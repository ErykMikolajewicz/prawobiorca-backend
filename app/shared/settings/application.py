from enum import StrEnum
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class HttpClientType(StrEnum):
    HTTPX = "HTTPX"


class ApplicationSettings(BaseSettings):
    LOGGING_LEVEL: str = ...

    SESSION_ID_EXPIRATION_SECONDS: int = ...

    HTTP_CLIENT: HttpClientType = ...

    EMBED_DOCS_CHUNK_SIZE: int = 10

    DOCUMENT_DESIRED_TOKENS_LENGTH: int = Field(default_factory=int, gt=0)

    model_config = SettingsConfigDict(
        env_file=Path(".env"), extra="ignore", case_sensitive=True, frozen=True, env_prefix="APP_"
    )


app_settings = ApplicationSettings()

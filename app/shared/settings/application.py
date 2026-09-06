from enum import StrEnum
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class HttpClientType(StrEnum):
    HTTPX = "HTTPX"


class ApplicationSettings(BaseSettings):
    LOGGING_LEVEL: str = ...

    JWT_SECRET_KEY: SecretStr = Field(..., min_length=32)

    JWT_ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRATION_SECONDS: int = Field(default=900, gt=0)

    REFRESH_TOKEN_EXPIRATION_SECONDS: int = Field(default=1209600, gt=0)

    COOKIE_SECURE: bool = True

    COOKIE_SAMESITE: Literal["lax", "strict", "none"] = "lax"

    HTTP_CLIENT: HttpClientType = ...

    EMBED_DOCS_CHUNK_SIZE: int = 10

    DOCUMENT_DESIRED_TOKENS_LENGTH: int = Field(default_factory=int, gt=0)

    model_config = SettingsConfigDict(
        env_file=Path(".env"), extra="ignore", case_sensitive=True, frozen=True, env_prefix="APP_"
    )


app_settings = ApplicationSettings()

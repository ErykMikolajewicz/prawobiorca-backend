from enum import StrEnum
from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class FileStorageType(StrEnum):
    GOOGLE_CLOUD = "GOOGLE_CLOUD"
    LOCAL_FILES = "LOCAL_FILES"


class HttpClientType(StrEnum):
    HTTPX = "HTTPX"


class VectorDBType(StrEnum):
    QDRANT = "QDRANT"


class ApplicationSettings(BaseSettings):
    LOGGING_LEVEL: str = ...

    SESSION_KEY: SecretStr = ...

    ACCESS_TOKEN_EXPIRATION_SECONDS: int = ...
    REFRESH_TOKEN_EXPIRATION_SECONDS: int = ...

    FILE_STORAGE: FileStorageType = ...

    VECTOR_DB: VectorDBType = ...

    HTTP_CLIENT: HttpClientType = ...

    model_config = SettingsConfigDict(
        env_file=Path(".env"), extra="ignore", case_sensitive=True, frozen=True, env_prefix="APP_"
    )


app_settings = ApplicationSettings()

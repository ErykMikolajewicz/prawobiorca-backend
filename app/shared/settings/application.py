from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic.types import SecretStr

from app.infrastructure.enums import FileStorageType, HttpClientType


class ApplicationSettings(BaseSettings):
    LOGGING_LEVEL: str = ...

    SESSION_KEY: SecretStr = ...

    ACCESS_TOKEN_EXPIRATION_SECONDS: int = ...
    REFRESH_TOKEN_EXPIRATION_SECONDS: int = ...

    FILE_STORAGE: FileStorageType = ...

    HTTP_CLIENT: HttpClientType = ...

    model_config = SettingsConfigDict(
        env_file=Path(".env"), extra="ignore", case_sensitive=True, frozen=True, env_prefix="APP_"
    )


app_settings = ApplicationSettings()

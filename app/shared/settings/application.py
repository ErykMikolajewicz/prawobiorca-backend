from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.infrastructure.enums import FileStorageType, HttpClientType
import app.shared.consts as const


class ApplicationSettings(BaseSettings):
    LOGGING_LEVEL: str = ...

    ACCESS_TOKEN_EXPIRATION_SECONDS: int = ...
    
    REFRESH_TOKEN_EXPIRATION_SECONDS: int = ...

    FILE_STORAGE: FileStorageType = FileStorageType.LOCAL_FILES

    HTTP_CLIENT: HttpClientType = HttpClientType.HTTPX
    
    model_config = SettingsConfigDict(
        env_file=Path(".env"), extra="ignore", case_sensitive=True, frozen=True, env_prefix="APP_"
    )


app_settings = ApplicationSettings()

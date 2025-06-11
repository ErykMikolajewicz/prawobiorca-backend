from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

APPLICATION_SETTINGS_FILE_PATH = Path(".env")


class ApplicationSettings(BaseSettings):
    LOGGING_LEVEL: str
    ACCESS_TOKEN_EXPIRATION_SECONDS: int
    REFRESH_TOKEN_EXPIRATION_SECONDS: int
    CREATE_TABLES: bool

    model_config = SettingsConfigDict(
        env_file=APPLICATION_SETTINGS_FILE_PATH, env_file_encoding="utf-8", case_sensitive=True, frozen=True
    )

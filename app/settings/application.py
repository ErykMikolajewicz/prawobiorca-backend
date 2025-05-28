from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


APPLICATION_SETTINGS_FILE_PATH = Path('.env')


class ApplicationSettings(BaseSettings):
    LOGGING_LEVEL: str
    USER_TOKEN_EXPIRATION_SECONDS: int
    CREATE_TABLES: bool

    model_config = SettingsConfigDict(
        env_file=APPLICATION_SETTINGS_FILE_PATH,
        env_file_encoding="utf-8",
        case_sensitive=True,
        frozen=True
    )

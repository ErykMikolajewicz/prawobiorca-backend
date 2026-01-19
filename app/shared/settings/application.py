from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class ApplicationSettings(BaseSettings):
    LOGGING_LEVEL: str = ...
    ACCESS_TOKEN_EXPIRATION_SECONDS: int = ...
    REFRESH_TOKEN_EXPIRATION_SECONDS: int = ...

    model_config = SettingsConfigDict(
        env_file=Path(".env"), extra="ignore", case_sensitive=True, frozen=True, env_prefix="APP_"
    )


app_settings = ApplicationSettings()

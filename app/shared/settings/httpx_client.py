from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class HttpxClientSettings(BaseSettings):
    TIMEOUT: int = 10
    MAX_CONNECTIONS: int = 100
    MAX_KEEP_ALIVE_CONNECTIONS: int = 20

    model_config = SettingsConfigDict(
        env_file=Path(".env"), extra="ignore", case_sensitive=True, frozen=True, env_prefix="HTTPX_"
    )


httpx_client_settings = HttpxClientSettings()

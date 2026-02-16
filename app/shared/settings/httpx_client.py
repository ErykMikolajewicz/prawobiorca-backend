from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class HttpxClientSettings(BaseSettings):
    TIMEOUT: int = ...
    MAX_CONNECTIONS: int = ...
    MAX_KEEP_ALIVE_CONNECTIONS: int = ...

    model_config = SettingsConfigDict(
        env_file=Path(".env"), extra="ignore", case_sensitive=True, frozen=True, env_prefix="HTTPX_"
    )


httpx_client_settings = HttpxClientSettings()
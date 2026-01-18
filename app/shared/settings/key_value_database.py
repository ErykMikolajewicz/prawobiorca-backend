from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class RedisSettings(BaseSettings):
    HOST: str = ...
    PORT: int = ...
    DB_NUMBER: int = ...
    MAX_CONNECTIONS: int = ...

    model_config = SettingsConfigDict(
        env_file=Path(".env"), extra='ignore', case_sensitive=True, frozen=True, env_prefix='REDIS_'
    )

redis_settings = RedisSettings()

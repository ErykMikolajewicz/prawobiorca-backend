from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class RelationalDatabaseSettings(BaseSettings):
    DRIVER: str = "postgresql+asyncpg"
    USER: str = ...
    PASSWORD: str = ...
    HOST: str = ...
    PORT: int = ...
    NAME: str = ...
    POOL_SIZE: int = 50
    MAX_OVERFLOW: int = 20
    POOL_TIMEOUT: int = 30
    POOL_RECYCLE: int = 900

    model_config = SettingsConfigDict(
        env_file=Path(".env"),
        extra="forbid",
        dotenv_filtering="match_prefix",
        case_sensitive=True,
        frozen=True,
        env_prefix="RELATIONAL_DB_",
    )


relational_db_settings = RelationalDatabaseSettings()

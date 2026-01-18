from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

RELATIONAL_DB_SETTINGS_FILE_PATH = Path("config") / "relational_db.env"


class RelationalDatabaseSettings(BaseSettings):
    DRIVER: str
    DB_USER: str
    PASSWORD: str
    HOST: str
    PORT: int
    DB_NAME: str
    POOL_SIZE: int
    MAX_OVERFLOW: int
    POOL_TIMEOUT: int
    POOL_RECYCLE: int

    model_config = SettingsConfigDict(
        env_file=RELATIONAL_DB_SETTINGS_FILE_PATH, env_file_encoding="utf-8", case_sensitive=True, frozen=True
    )

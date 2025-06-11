from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

VECTOR_DB_SETTINGS_FILE_PATH = Path("config") / "vector_db.env"


class VectorDatabaseSettings(BaseSettings):
    HOST: str
    GRPC_PORT: int

    model_config = SettingsConfigDict(
        env_file=VECTOR_DB_SETTINGS_FILE_PATH, env_file_encoding="utf-8", case_sensitive=True, frozen=True
    )

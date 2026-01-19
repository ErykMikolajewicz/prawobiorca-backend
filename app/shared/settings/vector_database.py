from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

VECTOR_DB_SETTINGS_FILE_PATH = Path("config") / "vector_db.env"


class QdrantSettings(BaseSettings):
    HOST: str = ...
    GRPC_PORT: int = ...

    model_config = SettingsConfigDict(
        env_file=Path(".env"), extra="ignore", case_sensitive=True, frozen=True, env_prefix="QDRANT_"
    )


qdrant_settings = QdrantSettings()

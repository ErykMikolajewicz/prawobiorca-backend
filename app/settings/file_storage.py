from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


FILE_STORAGE_SETTINGS_FILE_PATH = Path("config") / "file_storage.env"


class FileStorageSettings(BaseSettings):
    STORAGE_CREDENTIALS: Path
    PRIVATE_COLLECTION: str
    PUBLIC_COLLECTION: str

    model_config = SettingsConfigDict(
        env_file=FILE_STORAGE_SETTINGS_FILE_PATH, env_file_encoding="utf-8", case_sensitive=True, frozen=True
    )

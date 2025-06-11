from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

CLOUD_STORAGE_SETTINGS_FILE_PATH = Path("config") / "cloud_storage.env"


class CloudStorageSettings(BaseSettings):
    GOOGLE_APPLICATION_CREDENTIALS: Path
    BUCKET_NAME: str

    model_config = SettingsConfigDict(
        env_file=CLOUD_STORAGE_SETTINGS_FILE_PATH, env_file_encoding="utf-8", case_sensitive=True, frozen=True
    )

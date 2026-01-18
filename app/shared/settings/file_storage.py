from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class GCFileStorageSettings(BaseSettings):
    STORAGE_CREDENTIALS: Path = ...
    PRIVATE_COLLECTION: str = ...
    PUBLIC_COLLECTION: str = ...

    model_config = SettingsConfigDict(
        env_file=Path(".env"), extra='ignore', case_sensitive=True, frozen=True, env_prefix='GC_'
    )


gc_file_storage_settings = GCFileStorageSettings()

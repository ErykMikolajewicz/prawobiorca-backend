from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


KEY_VALUE_DB_SETTINGS_FILE_PATH = Path('config') / "key_value_db.env"


class KeyValueDatabaseSettings(BaseSettings):
    HOST: str
    PORT: int
    DB_NUMBER: int
    MAX_CONNECTIONS: int

    model_config = SettingsConfigDict(
        env_file=KEY_VALUE_DB_SETTINGS_FILE_PATH,
        env_file_encoding="utf-8",
        case_sensitive=True,
        frozen=True
    )
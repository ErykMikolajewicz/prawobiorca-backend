from pydantic_settings import BaseSettings, SettingsConfigDict

from app.shared.settings.application import ApplicationSettings
from app.shared.settings.file_storage import FileStorageSettings
from app.shared.settings.key_value_database import KeyValueDatabaseSettings
from app.shared.settings.relational_database import RelationalDatabaseSettings
from app.shared.settings.vector_database import VectorDatabaseSettings


class Settings(BaseSettings):
    relational_db: RelationalDatabaseSettings = RelationalDatabaseSettings()
    vector_db: VectorDatabaseSettings = VectorDatabaseSettings()
    app: ApplicationSettings = ApplicationSettings()
    key_value_db: KeyValueDatabaseSettings = KeyValueDatabaseSettings()
    file_storage: FileStorageSettings = FileStorageSettings()

    model_config = SettingsConfigDict(case_sensitive=True, frozen=True)


settings = Settings()

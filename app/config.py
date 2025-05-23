from pydantic_settings import BaseSettings, SettingsConfigDict

from app.settings.relational_database import RelationalDatabaseSettings
from app.settings.vector_database import VectorDatabaseSettings
from app.settings.application import ApplicationSettings


class Settings(BaseSettings):
    relational_db: RelationalDatabaseSettings = RelationalDatabaseSettings()
    vector_db: VectorDatabaseSettings = VectorDatabaseSettings()
    app: ApplicationSettings = ApplicationSettings()

    model_config = SettingsConfigDict(
        case_sensitive=True,
        frozen=True
    )

settings = Settings()

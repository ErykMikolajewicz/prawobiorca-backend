from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class TextTransformatorSettings(BaseSettings):
    URL: str = ...
    MAX_TOKENS: int = Field(default=..., gt=0)

    model_config = SettingsConfigDict(
        env_file=Path(".env"), extra="ignore", case_sensitive=True, frozen=True, env_prefix="TEXT_TRANSFORMATOR_"
    )


text_transformator_settings = TextTransformatorSettings()

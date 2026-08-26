from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class TokenizerSettings(BaseSettings):
    MAX_TOKENS: int = Field(default=2048, gt=0)
    MAX_TITLE_TOKENS_OVERHEAD: int = Field(default=16, ge=0)

    model_config = SettingsConfigDict(
        env_file=Path(".env"), extra="ignore", case_sensitive=True, frozen=True, env_prefix="TOKENIZER_"
    )


tokenizer_settings = TokenizerSettings()

from uuid import UUID

from pydantic import BaseModel, Field

from app.shared.consts import HASH_LENGTH_BASE64


class SearchResult(BaseModel):
    id: UUID
    text: str


class SearchParams(BaseModel):
    threshold: float = Field(ge=-1, le=1)
    limit: int | None = Field(default=None, gt=0)
    file_hash_str: str = Field(min_length=HASH_LENGTH_BASE64, max_length=HASH_LENGTH_BASE64, alias="fileHashStr")

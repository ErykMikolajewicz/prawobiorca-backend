from uuid import UUID

from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    id: UUID
    score: float = Field(ge=-1, le=1)
    text: str


class SearchParams(BaseModel):
    threshold: float = Field(ge=-1, le=1)
    limit: int | None = Field(default=None, gt=0)
    regulation_id: UUID = Field(alias="fileId")
    user_id: UUID | None = Field(alias="userId")

from uuid import UUID

from fastapi import Query
from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    id: UUID
    score: float = Field(ge=-1, le=1)
    header: str
    text: str


class SearchParams(BaseModel):
    threshold: float = Query(ge=-1, le=1)
    limit: int | None = Query(default=None, gt=0)
    query: str = Query()

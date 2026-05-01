from uuid import UUID

from pydantic import BaseModel


class SearchResult(BaseModel):
    id: UUID
    text: str

from enum import StrEnum
from uuid import UUID

from fastapi import Query
from pydantic import BaseModel, Field

from src.domain.value_objects.legal_units import UnitType


class SearchResultElement(BaseModel):
    text: str
    subsection: str | None = None


class SearchResult(BaseModel):
    id: UUID
    score: float = Field(ge=-1, le=1)
    header: str | None = None
    text: str
    unit_type: UnitType | None = None
    unit_number: str | None = None
    unit_path: list[str] | None = None
    elements: list[SearchResultElement] | None = None


class SearchOrder(StrEnum):
    DOCUMENT = "document"
    SCORE = "score"


class SearchParams(BaseModel):
    threshold: float = Query(ge=-1, le=1)
    limit: int | None = Query(default=None, gt=0)
    query: str = Query()
    order_by: SearchOrder = Query(default=SearchOrder.DOCUMENT)

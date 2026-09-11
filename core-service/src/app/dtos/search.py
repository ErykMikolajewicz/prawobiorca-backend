from uuid import UUID

from fastapi import Query
from pydantic import BaseModel, Field

from src.domain.value_objects.legal_units import UnitType


class SearchResult(BaseModel):
    id: UUID
    score: float = Field(ge=-1, le=1)
    header: str | None = None
    text: str
    unit_type: UnitType | None = None
    unit_number: str | None = None
    unit_path: list[str] | None = None
    part_index: int = 1
    parts_total: int = 1


class SearchParams(BaseModel):
    threshold: float = Query(ge=-1, le=1)
    limit: int | None = Query(default=None, gt=0)
    query: str = Query()

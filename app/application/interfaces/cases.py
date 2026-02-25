from datetime import datetime
from typing import Protocol
from uuid import UUID

from pydantic import BaseModel


class CaseData(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    context: str | None = None
    create_date: datetime


class CasesRepository(Protocol):
    async def list_by_user_id(self, user_id: UUID) -> list[CaseData]: ...

    async def add(self, user_id: UUID, name: str, context: str | None = None) -> UUID: ...

    async def delete(self, case_id: UUID, user_id: UUID) -> None: ...

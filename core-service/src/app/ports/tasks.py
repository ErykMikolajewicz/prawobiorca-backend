from typing import Protocol
from uuid import UUID


class RegulationPreparationScheduler(Protocol):
    async def schedule_regulation_preparation(self, user_id: UUID | None, regulation_id: UUID) -> None: ...

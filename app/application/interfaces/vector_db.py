from typing import Protocol
from uuid import UUID


class RegulationsRepository(Protocol):
    async def add_point(
        self, 
        point_id: UUID, 
        vector: list[float], 
        payload: dict
    ) -> None: ...

    async def search(
        self,
        vector: list[float],
        limit: int,
        threshold: float,
    ) -> list[dict]: ...

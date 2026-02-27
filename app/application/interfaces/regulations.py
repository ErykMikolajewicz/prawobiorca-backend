from typing import Protocol

from app.domain.value_objects.documents import EmbeddedDocument


class RegulationsRepository(Protocol):
    async def add_documents(self, documents: list[EmbeddedDocument]) -> None: ...

    async def search(
        self,
        vector: list[float],
        limit: int,
        threshold: float,
    ) -> list[dict]: ...

    async def initialize_law_act(self, act_name: str): ...

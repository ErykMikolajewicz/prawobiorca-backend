from typing import Protocol

from app.domain.value_objects.documents import DocumentsCollection


class UserRegulationsRepository(Protocol):
    async def add_documents(self, documents: DocumentsCollection) -> None: ...

    async def search(
        self,
        vector: list[float],
        limit: int,
        threshold: float,
    ) -> list[dict]: ...

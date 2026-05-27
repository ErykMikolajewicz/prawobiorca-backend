from typing import Protocol
from uuid import UUID

from app.application.dtos.search import SearchParams, SearchResult
from app.application.interfaces.relational import AsyncSession
from app.domain.value_objects.documents import DocumentsCollection


class DocumentsRepository(Protocol):
    async def add_documents(
        self, session: AsyncSession, user_id: UUID | None, regulation_id: UUID, documents: DocumentsCollection
    ) -> None: ...

    async def search(
        self,
        session: AsyncSession,
        user_id: UUID | None,
        regulation_id: UUID,
        vector: list[float],
        search_params: SearchParams,
    ) -> list[SearchResult]: ...

    async def remove_documents(self, session: AsyncSession, user_id: UUID | None, regulation_id: UUID) -> None: ...

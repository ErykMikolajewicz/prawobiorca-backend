from typing import Protocol

from app.application.dtos.search import SearchParams, SearchResult
from app.domain.value_objects.documents import DocumentsCollection


class UserRegulationsRepository(Protocol):
    async def add_documents(self, source_file_hash: str, documents: DocumentsCollection) -> None: ...

    async def search(self, vector: list[float], search_params: SearchParams) -> list[SearchResult]: ...

    async def remove_documents(self, source_file_hash: str) -> None: ...


class PublicRegulationsRepository(Protocol):
    async def search(self, vector: list[float], search_params: SearchParams) -> list[SearchResult]: ...

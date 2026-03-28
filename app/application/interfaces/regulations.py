from typing import Protocol

from app.domain.value_objects.documents import DocumentsCollection


class UserRegulationsRepository(Protocol):
    async def add_documents(self, source_file_hash: str, documents: DocumentsCollection) -> None: ...

    async def search(self, vector: list[float], limit: int, threshold: float, source_file_hash: str) -> list[dict]: ...


class PublicRegulationsRepository(Protocol):
    async def search(self, vector: list[float], limit: int, threshold: float, source_file_hash: str) -> list[dict]: ...

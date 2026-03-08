from collections.abc import Iterable
from typing import Protocol

from app.domain.value_objects.documents import DocumentsCollection


class EmbeddingPort(Protocol):
    async def embed_documents(self, documents: DocumentsCollection) -> list[list[float]]: ...

    async def embed_queries(self, queries: Iterable[str]) -> list[list[float]]: ...

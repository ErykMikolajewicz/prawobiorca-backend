from collections.abc import Iterable
from typing import Protocol

from app.domain.value_objects.preparation import DocumentToEmbed


class EmbeddingPort(Protocol):
    async def embed_documents(self, documents: Iterable[DocumentToEmbed]) -> list[list[float]]: ...

    async def embed_queries(self, queries: Iterable[str]) -> list[list[float]]: ...

from collections.abc import Iterable
from typing import Protocol


class EmbeddingPort(Protocol):
    async def embed_documents(self, documents: Iterable[str], title: str) -> list[list[float]]: ...

    async def embed_queries(self, queries: Iterable[str]) -> list[list[float]]: ...

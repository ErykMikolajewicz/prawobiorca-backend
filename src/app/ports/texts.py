from collections.abc import Iterable
from typing import Protocol

from src.domain.value_objects.documents import Document


class TextsEmbedder(Protocol):
    async def embed_documents(self, documents: Iterable[Document]) -> list[list[float]]: ...

    async def embed_queries(self, queries: Iterable[str]) -> list[list[float]]: ...

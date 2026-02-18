from typing import Iterable

from httpx import AsyncClient


class HttpxEmbeddingsPort:
    def __init__(self, client: AsyncClient, embedding_url: str):
        self._client = client
        self._embedding_url = embedding_url

    async def embed_documents(self, documents: Iterable[str], title: str | None = None) -> list[list[float]]:
        if title:
            prefix = f"title: {title} | text: "
        else:
            prefix = "text: "

        documents_with_prefix = [prefix + document for document in documents]

        response = await self._client.post(self._embedding_url, json=documents_with_prefix)
        embeddings = response.json()

        return embeddings

    async def embed_queries(self, queries: Iterable[str]) -> list[list[float]]:
        prefix = "task: search result | query: "

        queries_with_prefix = [prefix + query for query in queries]

        response = await self._client.post(self._embedding_url, json=queries_with_prefix)
        embeddings = response.json()

        return embeddings

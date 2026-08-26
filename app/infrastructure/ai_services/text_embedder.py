from typing import Iterable

from httpx2 import AsyncClient

from app.domain.value_objects.documents import Document


class TextsEmbedder:
    def __init__(self, client: AsyncClient, embedding_service_url: str):
        self._client = client
        self._embedding_url = f"{embedding_service_url}/embed"

    async def embed_documents(self, documents: Iterable[Document]) -> list[list[float]]:
        prefixed_docs = []
        for document in documents:
            title = document.title
            if title is None:
                title = "none"

            prefix = f"title: {title} | text: "
            prefixed_docs.append(prefix + document.text)

        response = await self._client.post(self._embedding_url, json=prefixed_docs)
        embeddings = response.json()

        return embeddings

    async def embed_queries(self, queries: Iterable[str]) -> list[list[float]]:
        prefix = "task: search result | query: "

        queries_with_prefix = [prefix + query for query in queries]

        response = await self._client.post(self._embedding_url, json=queries_with_prefix)
        embeddings = response.json()

        return embeddings

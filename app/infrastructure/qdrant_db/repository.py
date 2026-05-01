from uuid import UUID

from grpc.aio import AioRpcError
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import FieldCondition, Filter, MatchValue, PointStruct

from app.application.dtos.search import SearchResult
from app.domain.exceptions import RegulationsNotPreparedToSearch
from app.domain.value_objects.documents import DocumentsCollection
from app.shared.consts import VECTOR_DB_PUBLIC_COLLECTION_NAME, VECTOR_DB_USERS_COLLECTION_NAME


class QdrantUserRegulationsRepository:
    _collection_name = VECTOR_DB_USERS_COLLECTION_NAME

    def __init__(self, client: AsyncQdrantClient, user_id: UUID):
        self._client = client
        self._user_id = str(user_id)

    async def add_documents(self, source_file_hash: str, documents: DocumentsCollection) -> None:
        points = []
        for document in documents:
            payload = {
                "text": document.text,
                "user_id": self._user_id,
                "source_file_hash": source_file_hash,
            }
            point = PointStruct(
                id=str(document.id),
                vector=document.vector,
                payload=payload,
            )
            points.append(point)

        await self._client.upsert(collection_name=self._collection_name, points=points)

    async def search(
        self, vector: list[float], limit: int, threshold: float, source_file_hash: str
    ) -> list[SearchResult]:

        query_filter = Filter(
            must=[
                FieldCondition(key="user_id", match=MatchValue(value=self._user_id)),
                FieldCondition(key="source_file_hash", match=MatchValue(value=source_file_hash)),
            ]
        )

        try:
            search_result = await self._client.query_points(
                collection_name=self._collection_name,
                query=vector,
                limit=limit,
                score_threshold=threshold,
                query_filter=query_filter,
            )
        except AioRpcError:
            raise RegulationsNotPreparedToSearch(self._collection_name)

        results = []
        for point in search_result.points:
            text = point.payload["text"]
            result = SearchResult(id=point.id, text=text)
            results.append(result)

        return results

    async def remove_documents(self, source_file_hash: str) -> None:
        delete_selector = Filter(
            must=[
                FieldCondition(key="user_id", match=MatchValue(value=self._user_id)),
                FieldCondition(key="source_file_hash", match=MatchValue(value=source_file_hash)),
            ]
        )

        await self._client.delete(collection_name=self._collection_name, points_selector=delete_selector)


class QdrantPublicRegulationsRepository:
    _collection_name = VECTOR_DB_PUBLIC_COLLECTION_NAME

    def __init__(self, client: AsyncQdrantClient):
        self._client = client

    async def search(
        self, vector: list[float], limit: int, threshold: float, source_file_hash: str
    ) -> list[SearchResult]:
        query_filter = Filter(must=[FieldCondition(key="source_file_hash", match=MatchValue(value=source_file_hash))])

        try:
            search_result = await self._client.query_points(
                collection_name=self._collection_name,
                query=vector,
                limit=limit,
                score_threshold=threshold,
                query_filter=query_filter,
            )
        except AioRpcError:
            raise RegulationsNotPreparedToSearch(self._collection_name)

        results = []
        for point in search_result.points:
            text = point.payload["text"]
            result = SearchResult(id=point.id, text=text)
            results.append(result)

        return results

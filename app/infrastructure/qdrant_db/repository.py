from uuid import UUID

from grpc.aio import AioRpcError
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import PointStruct

from app.domain.exceptions import RegulationsNotPreparedToSearch
from app.domain.value_objects.documents import DocumentsCollection
from app.shared.consts import VECTOR_DB_USERS_COLLECTION_NAME


class QdrantUserRegulationsRepository:
    _collection_name = VECTOR_DB_USERS_COLLECTION_NAME

    def __init__(self, client: AsyncQdrantClient, user_id: UUID):
        self._client = client
        self._user_id = str(user_id)

    async def add_documents(self, documents: DocumentsCollection) -> None:
        points = []
        for document in documents:
            payload = {
                "text": document.text,
                "user_id": self._user_id,
                "source_file_hash": documents.source_file_hash_str,
            }
            point = PointStruct(
                id=str(document.id),
                vector=document.vector,
                payload=payload,
            )
            points.append(point)

        await self._client.upsert(collection_name=self._collection_name, points=points)

    async def search(
        self,
        vector: list[float],
        limit: int,
        threshold: float,
    ) -> list[dict]:
        try:
            search_result = await self._client.query_points(
                collection_name=self._collection_name,
                query=vector,
                limit=limit,
                score_threshold=threshold,
            )
        except AioRpcError:
            raise RegulationsNotPreparedToSearch(self._collection_name)

        results = []
        for point in search_result.points:
            results.append(point.payload)

        return results

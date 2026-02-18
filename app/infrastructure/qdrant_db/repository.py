from uuid import UUID

from grpc.aio import AioRpcError
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import PointStruct

from app.domain.exceptions import VectorCollectionNotFound


class QdrantRegulationsRepository:
    def __init__(self, client: AsyncQdrantClient, collection_name: str):
        self._client = client
        self._collection_name = collection_name

    async def add_point(self, point_id: UUID, vector: list[float], payload: dict) -> None:
        await self._client.upsert(
            collection_name=self._collection_name,
            points=[
                PointStruct(
                    id=str(point_id),
                    vector=vector,
                    payload=payload,
                )
            ],
        )

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
            raise VectorCollectionNotFound(self._collection_name)

        results = []
        for point in search_result:
            point = point[1]
            if point:
                results.append(point.payload)

        return results

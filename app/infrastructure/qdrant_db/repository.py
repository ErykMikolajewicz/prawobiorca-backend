from grpc.aio import AioRpcError
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from app.domain.exceptions import RegulationAlreadyInitialized, RegulationsNotPreparedToSearch
from app.domain.value_objects.documents import EmbeddedDocument


class QdrantRegulationsRepository:
    def __init__(self, client: AsyncQdrantClient, collection_name: str):
        self._client = client
        self._collection_name = collection_name

    async def add_documents(self, documents: list[EmbeddedDocument]) -> None:

        points = []
        for document in documents:
            point = PointStruct(
                id=str(document.id),
                vector=document.vector,
                payload=document.payload,
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

    async def initialize_law_act(self, act_name: str):
        vectors_config = VectorParams(size=768, distance=Distance.COSINE)
        try:
            await self._client.create_collection(act_name, vectors_config)
        except AioRpcError:
            raise RegulationAlreadyInitialized

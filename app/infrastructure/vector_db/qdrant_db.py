from qdrant_client import AsyncQdrantClient

from app.shared.settings.vector_database import qdrant_settings

qdrant_client: AsyncQdrantClient = AsyncQdrantClient(
    host=qdrant_settings.HOST, grpc_port=qdrant_settings.GRPC_PORT, prefer_grpc=True, https=False
)


async def get_qdrant_client():
    return qdrant_client

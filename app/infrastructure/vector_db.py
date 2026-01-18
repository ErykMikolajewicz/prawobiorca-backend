from qdrant_client import AsyncQdrantClient

from app.shared.config import settings

qdrant_client: AsyncQdrantClient = AsyncQdrantClient(
    host=settings.vector_db.HOST, grpc_port=settings.vector_db.GRPC_PORT, prefer_grpc=True, https=False
)


async def check_vector_db_connection():
    await qdrant_client.get_collections()


async def get_qdrant_client():
    return qdrant_client

import asyncio
import sys

sys.path.append(".")

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams

from app.shared.consts import VECTOR_DB_PUBLIC_COLLECTION_NAME, VECTOR_DB_USERS_COLLECTION_NAME
from app.shared.settings.qdrant_database import qdrant_settings

qdrant_client: AsyncQdrantClient = AsyncQdrantClient(
    host=qdrant_settings.HOST, grpc_port=qdrant_settings.GRPC_PORT, prefer_grpc=True, https=False
)


async def initialize_vector_db():
    vectors_config = VectorParams(size=768, distance=Distance.COSINE)

    await qdrant_client.create_collection(VECTOR_DB_USERS_COLLECTION_NAME, vectors_config)
    await qdrant_client.create_collection(VECTOR_DB_PUBLIC_COLLECTION_NAME, vectors_config)


if __name__ == "__main__":
    asyncio.run(initialize_vector_db())

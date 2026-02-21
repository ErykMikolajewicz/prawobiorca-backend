from qdrant_client import AsyncQdrantClient

from app.shared.settings.qdrant_database import qdrant_settings

qdrant_client: AsyncQdrantClient = AsyncQdrantClient(
    host=qdrant_settings.HOST, grpc_port=qdrant_settings.GRPC_PORT, prefer_grpc=True, https=False
)

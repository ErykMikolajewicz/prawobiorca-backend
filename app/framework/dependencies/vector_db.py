from typing import Awaitable, Callable

from app.infrastructure.qdrant_db.connection import qdrant_client
from app.shared.settings.application import VectorDBType, app_settings


async def check_vector_db_connection() -> Callable[..., Awaitable[None]]:
    match app_settings.VECTOR_DB:
        case VectorDBType.QDRANT:
            await qdrant_client.get_collections()
            return qdrant_client.close
        case _:
            raise Exception(f"Invalid config value, no such vector db type: {app_settings.VECTOR_DB} !")

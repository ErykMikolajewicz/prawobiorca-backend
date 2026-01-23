from typing import Callable, Awaitable

from app.infrastructure.vector_db.qdrant_db import qdrant_client


async def check_vector_db_connection() -> Callable[..., Awaitable[None]]:
    await qdrant_client.get_collections()
    return qdrant_client.close

from typing import Any, Awaitable, Callable

from app.infrastructure.object_storage.connection import init_object_storage_client


async def init_file_storage_client() -> tuple[Any, Callable[..., Awaitable[None]]]:
    return await init_object_storage_client()

from typing import Any, Awaitable, Callable

from fastapi.concurrency import run_in_threadpool

from app.shared.settings.application import FileStorageType, app_settings


async def init_file_storage_client() -> tuple[Any, Callable[..., Awaitable[None]]]:
    match app_settings.FILE_STORAGE:
        case FileStorageType.ON_PREMISE:
            from app.infrastructure.object_storage.on_premise.connection import init_object_storage_client

            return await init_object_storage_client()
        case FileStorageType.GOOGLE_CLOUD:
            from app.infrastructure.object_storage.gcp.repository import storage_client

            await run_in_threadpool(storage_client.list_buckets())

            async def closing_callback():
                await run_in_threadpool(storage_client.close)

            return storage_client, closing_callback
        case _:
            raise Exception(f"Invalid storage configuration {app_settings.FILE_STORAGE} !")

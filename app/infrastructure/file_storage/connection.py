from typing import Callable, Awaitable

from fastapi.concurrency import run_in_threadpool

from app.infrastructure.enums import FileStorageType
from app.shared.settings.application import app_settings


async def check_file_storage_connection() -> Callable[..., Awaitable[None]]:
    match app_settings.FILE_STORAGE:
        case FileStorageType.LOCAL_FILES:
            async def closing_callback():
                pass
            return closing_callback
        case FileStorageType.GOOGLE_CLOUD:
            from app.infrastructure.file_storage.gc.repository import storage_client

            await run_in_threadpool(storage_client.list_buckets())

            async def closing_callback():
                await run_in_threadpool(storage_client.close)

            return closing_callback
        case _:
            raise Exception(f"Invalid storage configuration {app_settings.FILE_STORAGE} !")

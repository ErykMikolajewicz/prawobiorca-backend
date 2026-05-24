from typing import Awaitable, Callable

from app.application.interfaces.file_storage import PublicFilesRepository
from fastapi import Request
from fastapi.concurrency import run_in_threadpool

from app.application.interfaces.regulations import RegulationsRepository
from app.shared.settings.application import FileStorageType, app_settings


def get_public_file_repository() -> PublicFilesRepository:
    match app_settings.FILE_STORAGE:
        case FileStorageType.LOCAL_FILES:
            from app.infrastructure.local_storage.repository import LocalPublicFileStorage

            return LocalPublicFileStorage()
        case FileStorageType.GOOGLE_CLOUD:
            from app.infrastructure.gc_storage.repository import GCSStorageRepository

            return GCSStorageRepository()
        case _:
            raise Exception(f"Invalid storage configuration {app_settings.FILE_STORAGE} !")


def get_users_file_repository(request: Request) -> RegulationsRepository:
    user_id = request.state.user_id
    # That dependency normally can be created only for logged users.
    # On the main page need to be created (and not used) with not logged users.
    if user_id is None:
        return None

    match app_settings.FILE_STORAGE:
        case FileStorageType.LOCAL_FILES:
            from app.infrastructure.local_storage.repository import LocalUsersFileStorage

            return LocalUsersFileStorage(user_id)
        case FileStorageType.GOOGLE_CLOUD:
            raise NotImplementedError
        case _:
            raise Exception(f"Invalid storage configuration {app_settings.FILE_STORAGE} !")


async def check_file_storage_connection() -> Callable[..., Awaitable[None]]:
    match app_settings.FILE_STORAGE:
        case FileStorageType.LOCAL_FILES:

            async def closing_callback():
                pass

            return closing_callback
        case FileStorageType.GOOGLE_CLOUD:
            from app.infrastructure.gc_storage.repository import storage_client

            await run_in_threadpool(storage_client.list_buckets())

            async def closing_callback():
                await run_in_threadpool(storage_client.close)

            return closing_callback
        case _:
            raise Exception(f"Invalid storage configuration {app_settings.FILE_STORAGE} !")

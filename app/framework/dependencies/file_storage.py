from app.domain.interfaces.file_storage import StorageRepository
from app.infrastructure.enums import FileStorageType
from app.shared.settings.application import app_settings


def get_file_storage() -> StorageRepository:
    match app_settings.FILE_STORAGE:
        case FileStorageType.LOCAL_FILES:
            from app.infrastructure.file_storage.local.repository import LocalFileStorage

            return LocalFileStorage()
        case FileStorageType.GOOGLE_CLOUD:
            from app.infrastructure.file_storage.gc.repository import GCSStorageRepository

            return GCSStorageRepository()
        case _:
            raise Exception(f"Invalid storage configuration {app_settings.FILE_STORAGE} !")

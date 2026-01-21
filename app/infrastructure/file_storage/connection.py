from app.infrastructure.enums import FileStorageType
from app.shared.settings.application import app_settings


def check_file_storage_connection():
    match app_settings.FILE_STORAGE:
        case FileStorageType.LOCAL_FILES:
            pass
        case FileStorageType.GOOGLE_CLOUD:
            from app.infrastructure.file_storage.gc.repository import storage_client

            storage_client.list_buckets()
        case _:
            raise Exception(f"Invalid storage configuration {app_settings.FILE_STORAGE} !")

import os

from fastapi.concurrency import run_in_threadpool
from google.cloud import storage
from google.cloud.storage import Blob

from app.application.dtos.files import FileData
from app.shared.settings.google_cloud_storage import gc_file_storage_settings

credentials_path = gc_file_storage_settings.STORAGE_CREDENTIALS
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(credentials_path.absolute())

storage_client = storage.Client()
bucket_name = gc_file_storage_settings.PRIVATE_COLLECTION


class GCSStorageRepository:
    def __init__(self):
        self.client = storage_client
        self.bucket = self.client.bucket("user_files")

    async def upload_file(self, file_data: FileData):
        blob: Blob = self.bucket.blob(file_data.name)
        await run_in_threadpool(blob.upload_from_string, file_data.file)

    async def delete_file(self, file_name: str) -> None:
        blob: Blob = self.bucket.blob(file_name)
        await run_in_threadpool(blob.delete)

    async def get_file(self, file_name: str) -> bytes:
        blob: Blob = self.bucket.blob(file_name)
        file = await run_in_threadpool(blob.download_as_bytes)
        return file

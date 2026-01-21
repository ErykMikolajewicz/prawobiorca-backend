import os
from typing import Optional

from fastapi import UploadFile
from fastapi.concurrency import run_in_threadpool
from google.cloud import storage
from google.cloud.storage import Blob

from app.shared.consts import DEFAULT_URL_EXPIRY
from app.shared.settings.file_storage import gc_file_storage_settings

credentials_path = gc_file_storage_settings.STORAGE_CREDENTIALS
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(credentials_path.absolute())

storage_client = storage.Client()
bucket_name = gc_file_storage_settings.PRIVATE_COLLECTION


class GCSStorageRepository:
    def __init__(self):
        self.client = storage_client
        self.bucket = self.client.bucket("user_files")
        self.default_url_expiry = DEFAULT_URL_EXPIRY

    async def upload_file(self, file_bytes: UploadFile, file_name: str) -> str:
        blob: Blob = self.bucket.blob(file_name)
        await run_in_threadpool(blob.upload_from_string, file_bytes.file)
        return await self.get_file_url(file_name)

    async def delete_file(self, file_name: str) -> None:
        blob: Blob = self.bucket.blob(file_name)
        await run_in_threadpool(blob.delete)

    async def get_file(self, file_name: str) -> bytes:
        blob: Blob = self.bucket.blob(file_name)
        file = await run_in_threadpool(blob.download_as_bytes)
        return file

    async def get_file_url(
        self,
        file_name: str,
        is_public: bool,
        expires_in: Optional[int] = None,
    ) -> str:
        blob: Blob = self.bucket.blob(file_name)
        if is_public:
            return blob.public_url
        expiry = expires_in or self.default_url_expiry
        return await run_in_threadpool(blob.generate_signed_url, expiration=expiry)

    async def list_files(
        self,
        prefix: Optional[str] = None,
    ) -> list[str]:
        def _list_blobs():
            return list(self.client.list_blobs(self.bucket, prefix=prefix))

        blobs = await run_in_threadpool(_list_blobs)
        return [blob.name for blob in blobs]

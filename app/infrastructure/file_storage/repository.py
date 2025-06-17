from typing import List, Optional

from fastapi import UploadFile
from fastapi.concurrency import run_in_threadpool
from google.cloud.storage import Blob

from app.infrastructure.file_storage.connection import get_storage_client
from app.shared.consts import DEFAULT_URL_EXPIRY


class GCSStorageRepository:
    def __init__(self, bucket_name: str, is_public: bool = False):
        self.client = get_storage_client()
        self.bucket = self.client.bucket(bucket_name)
        self.is_public = is_public
        self.default_url_expiry = DEFAULT_URL_EXPIRY

    async def upload_file(self, file_bytes: UploadFile, file_name: str) -> str:
        blob: Blob = self.bucket.blob(file_name)
        await run_in_threadpool(blob.upload_from_string, file_bytes.file)
        return await self.get_file_url(file_name)

    async def delete_file(self, file_name: str) -> None:
        blob: Blob = self.bucket.blob(file_name)
        await run_in_threadpool(blob.delete)

    async def get_file_url(
        self,
        file_name: str,
        expires_in: Optional[int] = None,
    ) -> str:
        blob: Blob = self.bucket.blob(file_name)
        if self.is_public:
            return blob.public_url
        expiry = expires_in or self.default_url_expiry
        return await run_in_threadpool(blob.generate_signed_url, expiration=expiry)

    async def list_files(
        self,
        prefix: Optional[str] = None,
    ) -> List[str]:
        def _list_blobs():
            return list(self.client.list_blobs(self.bucket, prefix=prefix))

        blobs = await run_in_threadpool(_list_blobs)
        return [blob.name for blob in blobs]

import asyncio

from google.cloud.storage import Client as StorageClient, Blob
from fastapi import UploadFile

from app.cloud_storage.connection import bucket_name

async def upload_file_to_cloud_storage(
    client: StorageClient,
    file_id: str,
    file: UploadFile
):

    bucket = client.bucket(bucket_name)
    blob: Blob = bucket.blob(file_id)

    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, blob.upload_from_file, file.file)

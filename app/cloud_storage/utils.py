from google.cloud.storage import Client as StorageClient, Blob
from fastapi import UploadFile
from fastapi.concurrency import run_in_threadpool

from app.cloud_storage.connection import bucket_name

async def upload_file_to_cloud_storage(
    client: StorageClient,
    file_id: str,
    file: UploadFile
):

    bucket = client.bucket(bucket_name)
    blob: Blob = bucket.blob(file_id)

    await run_in_threadpool(blob.upload_from_file, file.file)

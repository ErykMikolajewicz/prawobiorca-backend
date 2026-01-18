import os

from google.cloud import storage
from google.cloud.storage import Client as StorageClient

from app.shared.config import settings

credentials_path = settings.file_storage.STORAGE_CREDENTIALS
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(credentials_path.absolute())

storage_client = storage.Client()
bucket_name = settings.file_storage.PRIVATE_COLLECTION


def check_file_storage_connection():
    storage_client.list_buckets()


def get_storage_client() -> StorageClient:
    return storage_client

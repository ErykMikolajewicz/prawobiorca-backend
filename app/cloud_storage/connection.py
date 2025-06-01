import os

from google.cloud import storage
from google.cloud.storage import Client as StorageClient

from app.config import settings


credentials_path = settings.cloud_storage.GOOGLE_APPLICATION_CREDENTIALS
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(credentials_path.absolute())

storage_client = storage.Client()
bucket_name = settings.cloud_storage.BUCKET_NAME


def check_cloud_storage_connection():
    storage_client.list_buckets()


def get_storage_client() -> StorageClient:
    return storage_client

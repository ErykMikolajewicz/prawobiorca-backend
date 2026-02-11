from enum import StrEnum


class FileStorageType(StrEnum):
    GOOGLE_CLOUD = "GOOGLE_CLOUD"
    LOCAL_FILES = "LOCAL_FILES"


class HttpClientType(StrEnum):
    HTTPX = "HTTPX"


class VectorDBType(StrEnum):
    QDRANT = "QDRANT"

from typing import Optional

from fastapi import UploadFile
from fastapi.concurrency import run_in_threadpool


class LocalFileStorage:
    def __init__(self): ...

    async def upload_file(self, file_bytes: UploadFile, file_name: str) -> str:
        raise NotImplementedError

    async def delete_file(self, file_name: str) -> None:
        raise NotImplementedError

    async def get_file(self, file_name: str) -> bytes:
        raise NotImplementedError

    async def get_file_url(
        self,
        file_name: str,
        is_public: bool,
        expires_in: Optional[int] = None,
    ) -> str:
        raise NotImplementedError

    async def list_files(
        self,
        prefix: Optional[str] = None,
    ) -> list[str]:
        raise NotImplementedError

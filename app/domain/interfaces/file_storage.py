from typing import List, Optional, Protocol

from fastapi import UploadFile


class StorageRepository(Protocol):
    async def upload_file(
        self,
        file_bytes: UploadFile,
        file_name: str
    ) -> str:
        ...

    async def delete_file(self, file_name: str) -> None:
        ...

    async def get_file_url(
        self,
        file_name: str,
        expires_in: Optional[int] = None,
    ) -> str:
        ...

    async def list_files(
        self,
        prefix: Optional[str] = None,
    ) -> List[str]:
        ...

from typing import List, Optional, Protocol


class StorageRepository(Protocol):
    async def upload_file(self, file_bytes: bytes, file_name: str): ...

    async def delete_file(self, file_name: str) -> None: ...

    async def get_file(self, file_name: str) -> bytes: ...

    async def list_files(
        self,
        prefix: Optional[str] = None,
    ) -> List[str]: ...

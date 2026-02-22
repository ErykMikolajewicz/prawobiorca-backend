from typing import Protocol

from app.application.dtos.files import FileData


class StorageRepository(Protocol):
    async def upload_file(self, file_data: FileData): ...

    async def delete_file(self, file_name: str) -> None: ...

    async def get_file(self, file_name: str) -> bytes: ...

    async def list_files(
        self,
        prefix: str | None = None,
    ) -> list[str]: ...

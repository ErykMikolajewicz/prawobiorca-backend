from typing import Protocol

from app.application.dtos.files import FileData


class PublicFilesRepository(Protocol):
    async def get_file(self, file_name: str) -> bytes: ...


class UsersFilesRepository(Protocol):
    def __init__(self, user_id: str): ...

    async def get_file(self, file_name: str) -> bytes: ...

    async def upload_file(self, file_data: FileData): ...

    async def delete_file(self, file_name: str) -> None: ...

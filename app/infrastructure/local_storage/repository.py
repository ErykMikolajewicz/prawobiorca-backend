from pathlib import Path

import aiofiles
import aiofiles.os

from app.application.dtos.files import FileData


class LocalPublicFileStorage:
    _files_dir = Path("files/public")

    async def get_file(self, file_name: str) -> bytes:
        file_path = self._files_dir / file_name
        async with aiofiles.open(file_path, "rb") as file:
            bytes_read = await file.read()

        return bytes_read


class LocalUsersFileStorage:
    _users_dir = Path("files/users")

    def __init__(self, user_id: str):
        self._files_dir = self._users_dir / user_id

    async def upload_file(self, file_data: FileData):
        file_path = self._files_dir / file_data.name
        if file_path.exists():
            raise FileExistsError
        self._files_dir.mkdir(exist_ok=True)
        async with aiofiles.open(file_path, "wb") as file:
            await file.write(file_data.file)

    async def delete_file(self, file_name: str) -> None:
        file_path = self._files_dir / file_name
        await aiofiles.os.remove(file_path)

    async def get_file(self, file_name: str) -> bytes:
        file_path = self._files_dir / file_name
        async with aiofiles.open(file_path, "rb") as file:
            bytes_read = await file.read()

        return bytes_read

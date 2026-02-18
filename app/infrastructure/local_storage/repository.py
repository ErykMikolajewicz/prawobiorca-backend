from pathlib import Path
from typing import Optional

import aiofiles
import aiofiles.os

from app.shared.exceptions import FileNameExist


class LocalFileStorage:
    def __init__(self, files_dir="files"):
        self._files_dir = Path(files_dir)

    async def upload_file(self, file_bytes: bytes, file_name: str):
        file_path = self._files_dir / file_name
        if file_path.exists():
            raise FileNameExist(file_name)
        async with aiofiles.open(file_path, "wb") as file:
            await file.write(file_bytes)

    async def delete_file(self, file_name: str) -> None:
        file_path = self._files_dir / file_name
        await aiofiles.os.remove(file_path)

    async def get_file(self, file_name: str) -> bytes:
        file_path = self._files_dir / file_name
        async with aiofiles.open(file_path, "rb") as file:
            bytes_read = await file.read()

        return bytes_read

    async def list_files(
        self,
        prefix: Optional[str] = None,
    ) -> list[str]:

        if prefix:
            file_path = self._files_dir / prefix

        else:
            file_path = self._files_dir

        filenames = []
        for file in file_path.iterdir():
            filenames.append(file.name)

        return filenames

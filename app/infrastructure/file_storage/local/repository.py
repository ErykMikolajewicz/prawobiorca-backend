from pathlib import Path
from typing import Optional

import aiofiles

from app.shared.exceptions import FileNameExist


class LocalFileStorage:
    def __init__(self, files_dir="files"):
        self._files_dir = Path(files_dir)

    async def upload_file(self, file_bytes: bytes, file_name: str):
        file_path = self._files_dir / file_name
        if file_path.exists():
            raise FileNameExist
        async with aiofiles.open(file_path, "wb") as file:
            file.write(file_bytes)

    async def delete_file(self, file_name: str) -> None:
        raise NotImplementedError

    async def get_file(self, file_name: str) -> bytes:
        raise NotImplementedError

    async def list_files(
        self,
        prefix: Optional[str] = None,
    ) -> list[str]:
        raise NotImplementedError

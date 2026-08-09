from pathlib import Path
from uuid import UUID

import aiofiles
import aiofiles.os

from app.domain.exceptions.regulations import RegulationContentNotFound


class LocalRegulationsStorage:
    def __init__(self):
        self._regulations_dir = Path("regulations")

    async def get_regulation(self, id_: UUID) -> bytes:
        file_path = self._regulations_dir / str(id_)
        try:
            async with aiofiles.open(file_path, "rb") as file:
                bytes_read = await file.read()
        except FileNotFoundError:
            raise RegulationContentNotFound

        return bytes_read

    async def upload_regulation(self, id_: UUID, file_data: bytes):
        file_path = self._regulations_dir / str(id_)
        if file_path.exists():
            raise FileExistsError
        self._regulations_dir.mkdir(exist_ok=True)
        async with aiofiles.open(file_path, "wb") as file:
            await file.write(file_data)

    async def delete_regulation(self, id_: UUID) -> None:
        file_path = self._regulations_dir / str(id_)
        await aiofiles.os.remove(file_path)

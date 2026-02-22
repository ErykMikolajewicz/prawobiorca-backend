import logging
from dataclasses import dataclass

from app.application.dtos.files import FileData
from app.application.interfaces.file_storage import StorageRepository
from app.domain.exceptions import FileNameExist

logger = logging.getLogger(__name__)


@dataclass
class AddFile:
    file_data: FileData
    storage_repository: StorageRepository

    async def execute(self):
        try:
            await self.storage_repository.upload_file(self.file_data)
        except FileNameExist:
            logger.warning("File, with that name already exists!")
            raise


@dataclass
class ListFiles:
    storage_repository: StorageRepository

    async def execute(self) -> list[str]:
        files = await self.storage_repository.list_files()
        return files

import logging
from dataclasses import dataclass

from app.domain.interfaces.file_storage import StorageRepository
from app.shared.exceptions import EmptyFileException, FileNameExist, FileNameNotProvided

logger = logging.getLogger(__name__)


@dataclass
class AddUserFile:
    user_file: bytes
    file_name: str
    storage_repository: StorageRepository

    async def execute(self):
        if self.file_name == "":
            logger.warning("Tried to add file without name!")
            raise FileNameNotProvided

        if self.user_file == b"":
            logger.warning("Tried to add empty file!")
            raise EmptyFileException

        try:
            await self.storage_repository.upload_file(self.user_file, self.file_name)
        except FileNameExist:
            logger.warning("File, with that name already exists!")
            raise

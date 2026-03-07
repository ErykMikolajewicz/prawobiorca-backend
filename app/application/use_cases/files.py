import logging
from dataclasses import dataclass

from app.application.dtos.files import FileRepresentation
from app.application.interfaces.file_managment import PublicFileManager

logger = logging.getLogger(__name__)


@dataclass
class ListPublicFiles:
    file_manager: PublicFileManager

    async def execute(self) -> list[FileRepresentation]:
        files = await self.file_manager.list_all_files()
        return files

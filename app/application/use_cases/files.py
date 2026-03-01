import logging
from dataclasses import dataclass

from app.application.interfaces.file_storage import PublicFilesRepository

logger = logging.getLogger(__name__)


@dataclass
class ListPublicFiles:
    files_repository: PublicFilesRepository

    async def execute(self) -> list[str]:
        files = await self.files_repository.list_files()
        return files

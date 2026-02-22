from typing import Annotated

from fastapi import Depends

from app.application.interfaces.file_storage import StorageRepository
from app.application.use_cases.files import ListFiles
from app.framework.dependencies.file_storage import get_file_storage


async def get_list_files(storage_repository: Annotated[StorageRepository, Depends(get_file_storage)]) -> ListFiles:

    return ListFiles(storage_repository)

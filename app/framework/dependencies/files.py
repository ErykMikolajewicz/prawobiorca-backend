from typing import Annotated

from fastapi import Depends

from app.application.interfaces.file_storage import PublicFilesRepository
from app.application.use_cases.files import ListPublicFiles
from app.framework.dependencies.file_storage import get_public_file_repository


async def get_list_public_files(
    files_repository: Annotated[PublicFilesRepository, Depends(get_public_file_repository)],
) -> ListPublicFiles:

    return ListPublicFiles(files_repository)

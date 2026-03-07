from typing import Annotated

from fastapi import Depends

from app.application.interfaces.file_managment import PublicFileManager
from app.application.use_cases.files import ListPublicFiles
from app.framework.dependencies.file_managment import get_public_file_manager


async def get_list_public_files(
    file_manager: Annotated[PublicFileManager, Depends(get_public_file_manager)],
) -> ListPublicFiles:

    return ListPublicFiles(file_manager)

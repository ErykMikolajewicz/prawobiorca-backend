from typing import Annotated

from app.application.interfaces.file_managment import PublicFileManager
from app.application.use_cases.files import ListPublicFiles
from fastapi import Depends, Query

from app.domain.value_objects.regulations import RegulationType
from app.framework.dependencies.file_managment import get_public_file_manager


async def get_list_public_files(
    file_manager: Annotated[PublicFileManager, Depends(get_public_file_manager)],
    document_type: RegulationType | None = Query(default=None, alias="documentType"),
) -> ListPublicFiles:

    return ListPublicFiles(file_manager, document_type)

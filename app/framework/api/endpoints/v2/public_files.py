from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.application.dtos.files import FileRepresentation
from app.application.use_cases.files import ListPublicFiles
from app.framework.dependencies.files import get_list_public_files

public_files_router = APIRouter(tags=["public_fies"], prefix="/v2")


@public_files_router.get("/files", responses={status.HTTP_204_NO_CONTENT: {"description": "No public files."}})
async def get_public_files(
    list_public_files: Annotated[ListPublicFiles, Depends(get_list_public_files)],
) -> list[FileRepresentation]:
    public_files = await list_public_files.execute()

    if public_files:
        return public_files
    raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)

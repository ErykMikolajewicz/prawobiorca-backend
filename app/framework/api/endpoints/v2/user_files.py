from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.application.dtos.files import FileRepresentation
from app.application.use_cases.user_files import ListUserFiles
from app.framework.dependencies.authentication import set_user_by_session_id
from app.framework.dependencies.user_files import get_list_user_files

user_files_router = APIRouter(tags=["user_files"], dependencies=(Depends(set_user_by_session_id),), prefix="/v2")


@user_files_router.get("/user/files", responses={status.HTTP_204_NO_CONTENT: {"description": "No user files."}})
async def get_user_files(
    list_user_files: Annotated[ListUserFiles, Depends(get_list_user_files)],
) -> list[FileRepresentation]:
    user_files = await list_user_files.execute()
    if user_files:
        return user_files
    else:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="No user files.")

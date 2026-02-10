import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.application.use_cases.files import AddFile
from app.framework.dependencies.files import get_add_file
from app.shared.exceptions import EmptyFileException, FileNameExist, FileNameNotProvided

logger = logging.getLogger(__name__)

user_files_router = APIRouter(prefix="/user", tags=["user files"])


@user_files_router.post(
    "/files",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "File name not provided, or file is empty!"},
        status.HTTP_409_CONFLICT: {"description": "File with that name already exist!"},
    },
)
async def add_user_file(add_user_file_: Annotated[AddFile, Depends(get_add_file)]):
    try:
        await add_user_file_.execute()
    except EmptyFileException:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File can not be empty!")
    except FileNameNotProvided:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File name not provided!")
    except FileNameExist:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="File with that name already exist!")

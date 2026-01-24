import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.framework.dependencies.authentication import validate_token
from app.shared.exceptions import EmptyFileException, FileNameExist
from app.framework.dependencies.user_files import get_add_user_file
from app.application.use_cases.user_files import AddUserFile

logger = logging.getLogger(__name__)

user_files_router = APIRouter(prefix="/user", tags=["user files"], dependencies=[Depends(validate_token)])


@user_files_router.post(
    "/files",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "File name not provided!"},
        status.HTTP_409_CONFLICT: {"description": "File with that name already exist!"},
    },
)
async def add_user_file(add_user_file_: Annotated[AddUserFile, Depends(get_add_user_file)]):
    try:
        await add_user_file_.execute()
    except EmptyFileException:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File can not be empty!")
    except FileNameExist:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="File with that name already exist!")

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, status
from google.cloud.storage import Client as StorageClient

import app.domain.services.user_files as files_services
from app.infrastructure.cloud_storage.connection import get_storage_client
from app.dependencies.authentication import validate_token
from app.shared.exceptions import EmptyFileException, FileNameExist
from app.infrastructure.relational_db.units_of_work.users import UsersUnitOfWork
from app.dependencies.units_of_work import get_users_unit_of_work


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
async def add_user_file(
    user_file: UploadFile,
    request: Request,
    storage_client: Annotated[StorageClient, Depends(get_storage_client)],
    users_unit_of_work: UsersUnitOfWork = Depends(get_users_unit_of_work),
):
    user_id = request.state.user_id
    try:
        await files_services.add_user_file(users_unit_of_work, user_file, user_id, storage_client)
    except EmptyFileException:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File can not be empty!")
    except FileNameExist:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="File with that name already exist!")

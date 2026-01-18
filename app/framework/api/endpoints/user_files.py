import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, status

import app.domain.services.user_files as files_services
from app.domain.interfaces.file_storage import StorageRepository
from app.framework.dependencies.authentication import validate_token
from app.framework.dependencies.file_storage import storage_repo_factory
from app.framework.dependencies.units_of_work import get_users_unit_of_work
from app.infrastructure.relational_db.units_of_work.users import UsersUnitOfWork
from app.shared.exceptions import EmptyFileException, FileNameExist

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
    storage_repository: Annotated[StorageRepository, Depends(storage_repo_factory(is_public=False))],
    users_unit_of_work: UsersUnitOfWork = Depends(get_users_unit_of_work),
):
    user_id = request.state.user_id
    try:
        await files_services.add_user_file(users_unit_of_work, user_file, user_id, storage_repository)
    except EmptyFileException:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File can not be empty!")
    except FileNameExist:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="File with that name already exist!")

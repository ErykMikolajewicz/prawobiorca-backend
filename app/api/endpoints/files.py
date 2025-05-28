import logging

from fastapi import APIRouter, Depends, status, HTTPException, UploadFile

from app.units_of_work.users import UsersUnitOfWork
import app.services.user_files as files_services
from app.core.exceptions import NoFileName, FileNameExist
from app.core.authentication import validate_token


logger = logging.getLogger(__name__)

files_router = APIRouter(
    prefix="/files",
    tags=["files"],
    dependencies=[Depends(validate_token)]
)

@files_router.post("/user", status_code=status.HTTP_201_CREATED,
                     responses={ status.HTTP_400_BAD_REQUEST: {'description': 'File name not provided!'},
                         status.HTTP_409_CONFLICT: {'description': 'File with that name already exist!'}})
async def add_user_file(user_file: UploadFile, users_unit_of_work: UsersUnitOfWork = Depends()):
    try:
        await files_services.add_user_file(users_unit_of_work, user_file)
    except NoFileName:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='File name not provided!')
    except FileNameExist:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='File with that name already exist!')
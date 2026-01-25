from typing import Annotated

from fastapi import Depends, Request, UploadFile

from app.domain.interfaces.file_storage import StorageRepository
from app.framework.dependencies.file_storage import get_file_storage
from app.framework.dependencies.units_of_work import get_users_unit_of_work
from app.infrastructure.relational_db.units_of_work.users import UsersUnitOfWork
from app.application.use_cases.user_files import AddUserFile


def add_user_file_provider() -> type[AddUserFile]:
    return AddUserFile


def get_add_user_file(user_file: UploadFile,
    request: Request,
    storage_repository: Annotated[StorageRepository, Depends(get_file_storage)],
    users_unit_of_work: UsersUnitOfWork = Depends(get_users_unit_of_work),
    add_user_file: type[AddUserFile] = Depends(add_user_file_provider)) -> AddUserFile:
    return add_user_file()
from typing import Annotated

from fastapi import Depends, UploadFile

from app.application.use_cases.user_files import AddUserFile
from app.domain.interfaces.file_storage import StorageRepository
from app.framework.dependencies.file_storage import get_file_storage


def add_user_file_provider() -> type[AddUserFile]:
    return AddUserFile


async def get_add_user_file(
    user_file: UploadFile,
    storage_repository: Annotated[StorageRepository, Depends(get_file_storage)],
    add_user_file: type[AddUserFile] = Depends(add_user_file_provider),
) -> AddUserFile:
    file_bytes = await user_file.read()
    file_name = user_file.filename

    return add_user_file(file_bytes, file_name, storage_repository)

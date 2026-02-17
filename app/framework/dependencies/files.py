from typing import Annotated

from fastapi import Depends, UploadFile

from app.application.use_cases.files import AddFile, ListFiles
from app.application.interfaces.file_storage import StorageRepository
from app.framework.dependencies.file_storage import get_file_storage


def add_file_provider() -> type[AddFile]:
    return AddFile


async def get_add_file(
    file: UploadFile,
    storage_repository: Annotated[StorageRepository, Depends(get_file_storage)],
    add_file: Annotated[type[AddFile], Depends(add_file_provider)],
) -> AddFile:
    file_bytes = await file.read()
    file_name = file.filename

    return add_file(file_bytes, file_name, storage_repository)


def list_files_provider() -> type[ListFiles]:
    return ListFiles


async def get_list_files(
    storage_repository: Annotated[StorageRepository, Depends(get_file_storage)],
    list_files: Annotated[type[ListFiles], Depends(list_files_provider)],
) -> ListFiles:

    return list_files(storage_repository)

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Request, UploadFile, status
from fastapi.responses import RedirectResponse

from app.application.dtos.files import FileData
from app.application.interfaces.file_storage import UsersFilesRepository
from app.application.use_cases.user_files import AddUserFile, PrepareUserFile
from app.domain.exceptions import (
    FileNameExist,
    FileNameTooLong,
    InvalidCharacterInFileName,
    RegulationAlreadyInitialized,
)
from app.framework.dependencies.authentication import set_user_by_session_id
from app.framework.dependencies.file_storage import get_users_file_repository
from app.framework.dependencies.user_files import get_prepare_user_file
from app.shared.consts import FLASH_KEY

user_files_router = APIRouter(tags=["user_files"], dependencies=(Depends(set_user_by_session_id),))


@user_files_router.post("/user/files/{fileName}/preparation")
async def prepare_user_file(
    request: Request,
    prepare_user_file_: Annotated[PrepareUserFile, Depends(get_prepare_user_file)],
    file_name: str = Path(..., alias="fileName"),
):
    try:
        await prepare_user_file_.execute()
    except RegulationAlreadyInitialized:
        request.session[FLASH_KEY] = {"error_message": f"Plik o nazwie: {file_name} jest już przygotowany!"}
    else:
        request.session[FLASH_KEY] = {"info_message": f"Przygotowano plik {file_name}!"}

    return RedirectResponse(url=f"/files/search?filename={file_name}", status_code=status.HTTP_303_SEE_OTHER)


@user_files_router.post("/user/files")
async def add_file(
    request: Request,
    file: UploadFile,
    storage_repository: Annotated[UsersFilesRepository, Depends(get_users_file_repository)],
):
    file_bytes = await file.read()
    file_name = file.filename
    try:
        file_data = FileData(file_name=file_name, file=file_bytes)
    except ValueError:
        request.session[FLASH_KEY] = {"error_message": f"Plik {file_name} jest pusty, nie można dodać pustego pliku!"}
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    except FileNameTooLong:
        request.session[FLASH_KEY] = {"error_message": f"Nazwa {file_name} jest zbyt długa!"}
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    except InvalidCharacterInFileName:
        request.session[FLASH_KEY] = {"error_message": f"Nazwa {file_name} zawiera niedozwolone znaki!"}
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    add_file_ = AddUserFile(file_data, storage_repository)
    try:
        await add_file_.execute()
    except FileNameExist as e:
        request.session[FLASH_KEY] = {"error_message": f"Plik o nazwie {e.file_name} już istnieje, nie można go dodać!"}

    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

from typing import Annotated

from fastapi import APIRouter, Depends, Request, UploadFile, status
from fastapi.responses import RedirectResponse

from app.application.dtos.files import FileData
from app.application.interfaces.file_storage import StorageRepository
from app.application.use_cases.files import AddFile
from app.domain.exceptions import FileNameExist, FileNameTooLong, InvalidCharacterInFileName
from app.framework.dependencies.file_storage import get_file_storage
from app.shared.consts import FLASH_KEY

html_files_router = APIRouter(tags=["files"])


@html_files_router.post("/files")
async def add_file(
    request: Request, file: UploadFile, storage_repository: Annotated[StorageRepository, Depends(get_file_storage)]
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

    add_file_ = AddFile(file_data, storage_repository)
    try:
        await add_file_.execute()
    except FileNameExist as e:
        request.session[FLASH_KEY] = {"error_message": f"Plik o nazwie {e.file_name} już istnieje, nie można go dodać!"}

    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

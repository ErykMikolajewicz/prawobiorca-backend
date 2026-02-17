from typing import Annotated

from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import RedirectResponse

from app.application.use_cases.files import AddFile
from app.framework.dependencies.files import get_add_file
from app.shared.consts import FLASH_KEY
from app.shared.exceptions import EmptyFileException, FileNameExist, FileNameNotProvided

html_files_router = APIRouter(tags=["files"])


@html_files_router.post(
    "/files"
)
async def add_file(add_file_: Annotated[AddFile, Depends(get_add_file)], request: Request):
    try:
        await add_file_.execute()
    except EmptyFileException as e:
        request.session[FLASH_KEY] = {"error_message": f"Plik {e.file_name} jest pusty, nie można dodać pustego pliku!"}
    except FileNameExist as e:
        request.session[FLASH_KEY] = {"error_message": f"Plik o nazwie {e.file_name} już istnieje, nie można go dodać!"}
    except FileNameNotProvided:
        request.session[FLASH_KEY] = {"error_message": f"Próbowano dodać plik bez nazwy!"}

    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Request, status
from fastapi.responses import RedirectResponse

from app.application.use_cases.user_files import PrepareUserFile
from app.domain.exceptions import RegulationAlreadyInitialized
from app.framework.dependencies.user_files import get_prepare_user_file
from app.shared.consts import FLASH_KEY

user_files_router = APIRouter(tags=["user_files"])


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

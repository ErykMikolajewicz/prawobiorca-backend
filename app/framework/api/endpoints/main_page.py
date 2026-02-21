from typing import Annotated

from fastapi import APIRouter, Depends, Request, status

from app.application.use_cases.files import ListFiles
from app.framework.dependencies.authentication import set_user_by_session_id
from app.framework.dependencies.files import get_list_files
from app.framework.web.templating import templates
from app.shared.consts import FLASH_KEY

main_page_router = APIRouter(tags=["main_page"], dependencies=(Depends(set_user_by_session_id),))


@main_page_router.get(
    "/",
    status_code=status.HTTP_200_OK,
)
async def get_main_page(list_files: Annotated[ListFiles, Depends(get_list_files)], request: Request):
    files_list = await list_files.execute()

    flash_data = request.session.pop(FLASH_KEY, None)
    if flash_data:
        try:
            error_message = flash_data["error_message"]
        except KeyError:
            error_message = ""
    else:
        error_message = ""

    is_user_logged = request.state.user_id is not None

    return templates.TemplateResponse(
        "main_page.html",
        {"request": request, "files": files_list, "error_message": error_message, "is_user_logged": is_user_logged},
    )

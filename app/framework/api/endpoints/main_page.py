from typing import Annotated

from fastapi import APIRouter, Depends, Request, status

from app.application.use_cases.cases import ListCases
from app.application.use_cases.files import ListFiles
from app.framework.dependencies.authentication import set_user_by_session_id
from app.framework.dependencies.cases import get_list_user_cases
from app.framework.dependencies.files import get_list_files
from app.framework.web.helpers import render_page_template

main_page_router = APIRouter(tags=["main_page"], dependencies=(Depends(set_user_by_session_id),))


@main_page_router.get(
    "/",
    status_code=status.HTTP_200_OK,
)
async def get_main_page(
    list_files: Annotated[ListFiles, Depends(get_list_files)],
    list_cases: Annotated[ListCases, Depends(get_list_user_cases)],
    request: Request,
):
    files_list = await list_files.execute()

    is_user_logged = request.state.user_id is not None

    cases = []
    if is_user_logged:
        cases = await list_cases.execute()

    return render_page_template(request, "main_page.html", cases=cases, files=files_list)

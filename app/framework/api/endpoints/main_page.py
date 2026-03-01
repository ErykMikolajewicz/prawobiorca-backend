from typing import Annotated

from fastapi import APIRouter, Depends, Request, status

from app.application.use_cases.cases import ListCases
from app.application.use_cases.files import ListPublicFiles
from app.application.use_cases.user_files import ListUserFiles
from app.framework.dependencies.authentication import set_user_by_session_id
from app.framework.dependencies.cases import get_list_user_cases
from app.framework.dependencies.files import get_list_public_files
from app.framework.dependencies.user_files import get_list_user_files
from app.framework.web.helpers import render_page_template

main_page_router = APIRouter(tags=["main_page"], dependencies=(Depends(set_user_by_session_id),))


@main_page_router.get(
    "/",
    status_code=status.HTTP_200_OK,
)
async def get_main_page(
    list_public_files: Annotated[ListPublicFiles, Depends(get_list_public_files)],
    list_user_files: Annotated[ListUserFiles, Depends(get_list_user_files)],
    list_cases: Annotated[ListCases, Depends(get_list_user_cases)],
    request: Request,
):
    public_files = await list_public_files.execute()

    is_user_logged = request.state.user_id is not None

    if is_user_logged:
        cases = await list_cases.execute()
        user_files = await list_user_files.execute()
    else:
        cases, user_files = [], []

    response = render_page_template(
        request, "main_page.html", cases=cases, public_files=public_files, user_files=user_files
    )
    return response

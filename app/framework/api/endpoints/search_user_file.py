from typing import Annotated

from fastapi import APIRouter, Depends, Form, Query, Request, status
from fastapi.responses import RedirectResponse

from app.application.use_cases.cases import ListCases
from app.application.use_cases.search import SearchUserFile
from app.domain.exceptions import RegulationsNotPreparedToSearch
from app.framework.dependencies.authentication import set_user_by_session_id
from app.framework.dependencies.cases import get_list_user_cases
from app.framework.dependencies.search import get_search_user_file
from app.framework.web.helpers import render_page_template
from app.shared.consts import FLASH_KEY

user_file_search_router = APIRouter(
    tags=["search_user_file"], dependencies=(Depends(set_user_by_session_id),), prefix="/api"
)


@user_file_search_router.get("/search/user/file")
async def get_search_user_file_view(
    request: Request,
    list_cases: Annotated[ListCases, Depends(get_list_user_cases)],
    filename: Annotated[str, Query()],
    file_hash_str: Annotated[str, Query(alias="fileHashStr")],
    current_case_id: Annotated[str | None, Query()] = None,
):
    is_user_logged = request.state.user_id is not None

    if is_user_logged:
        cases = await list_cases.execute()
    else:
        cases = []

    return render_page_template(
        request,
        "search.html",
        filename=filename,
        file_hash_str=file_hash_str,
        cases=cases,
        current_case_id=current_case_id,
    )


@user_file_search_router.post(
    "/search/user/file",
    status_code=status.HTTP_200_OK,
)
async def post_search_user_file(
    request: Request,
    search_file: Annotated[SearchUserFile, Depends(get_search_user_file)],
    list_cases: Annotated[ListCases, Depends(get_list_user_cases)],
    query: Annotated[str, Form()],
    filename: Annotated[str, Form()],
    file_hash_str: Annotated[str, Form(alias="fileHashStr")],
    current_case_id: Annotated[str | None, Form()] = None,
):

    try:
        results = await search_file.execute()
    except RegulationsNotPreparedToSearch as e:
        error_message = f"Plik {e.regulations_name}, nie został przygotowany do przeszukiwania!"
        request.session[FLASH_KEY] = {"error_message": error_message}
        return RedirectResponse(url="/api/search/user/file", status_code=status.HTTP_303_SEE_OTHER)

    is_user_logged = request.state.user_id is not None

    if is_user_logged:
        cases = await list_cases.execute()
    else:
        cases = []

    results = [result.text for result in results]
    return render_page_template(
        request,
        "search.html",
        filename=filename,
        query=query,
        results=results,
        cases=cases,
        current_case_id=current_case_id,
        file_hash_str=file_hash_str,
    )

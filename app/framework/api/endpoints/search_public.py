from typing import Annotated

from fastapi import APIRouter, Depends, Form, Query, Request, status
from fastapi.responses import RedirectResponse

from app.application.use_cases.cases import ListCases
from app.application.use_cases.search import SearchPublicFile
from app.domain.exceptions import RegulationsNotPreparedToSearch
from app.framework.dependencies.authentication import set_user_by_session_id
from app.framework.dependencies.cases import get_list_user_cases
from app.framework.dependencies.search import get_search_public_file
from app.framework.web.helpers import render_page_template
from app.shared.consts import FLASH_KEY

public_search_router = APIRouter(tags=["search_public"], dependencies=(Depends(set_user_by_session_id),), prefix="/api")


@public_search_router.get("/search/public-file")
async def get_search_public_file_view(
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
        cases=cases,
        file_hash_str=file_hash_str,
        current_case_id=current_case_id,
    )


@public_search_router.post(
    "/search/public-file",
    status_code=status.HTTP_200_OK,
)
async def post_search_public_file(
    request: Request,
    list_cases: Annotated[ListCases, Depends(get_list_user_cases)],
    search_file: Annotated[SearchPublicFile, Depends(get_search_public_file)],
    query: Annotated[str, Form()],
    filename: Annotated[str, Form()],
    file_hash_str: Annotated[str, Form(alias="fileHashStr")],
    current_case_id: Annotated[str | None, Form()] = None,
):
    try:
        results = await search_file.execute()
    except RegulationsNotPreparedToSearch as e:
        error_message = (
            f"Nie przygotowano do wyszukiwania pliku {e.regulations_name}, zgłoś problem administratorowi aplikacji."
        )
        request.session[FLASH_KEY] = {"error_message": error_message}
        return RedirectResponse(url="/api/search/public-file", status_code=status.HTTP_303_SEE_OTHER)

    is_user_logged = request.state.user_id is not None

    if is_user_logged:
        cases = await list_cases.execute()
    else:
        cases = []

    return render_page_template(
        request,
        "search.html",
        filename=filename,
        query=query,
        results=results,
        cases=cases,
        file_hash_str=file_hash_str,
        current_case_id=current_case_id,
    )

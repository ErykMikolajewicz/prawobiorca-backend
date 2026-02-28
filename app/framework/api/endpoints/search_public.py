from typing import Annotated

from fastapi import APIRouter, Depends, Form, Query, Request, status
from fastapi.responses import RedirectResponse

from app.application.use_cases.search import SearchFile
from app.domain.exceptions import RegulationsNotPreparedToSearch
from app.framework.dependencies.authentication import set_user_by_session_id
from app.framework.dependencies.search import get_search_file
from app.framework.web.helpers import render_page_template
from app.shared.consts import FLASH_KEY

public_search_router = APIRouter(tags=["search_public"], dependencies=(Depends(set_user_by_session_id),))


@public_search_router.get(
    "/search/public-file",
    status_code=status.HTTP_200_OK,
)
async def get_search_public_file_view(request: Request, filename: str = Query()):
    return render_page_template(request, "search_public.html", filename=filename)


@public_search_router.post(
    "/search/public-file",
    status_code=status.HTTP_200_OK,
)
async def post_search_public_file(
    request: Request,
    search_file: Annotated[SearchFile, Depends(get_search_file)],
    query: str = Form(),
    filename: str = Query(),
):
    try:
        results = await search_file.execute()
    except RegulationsNotPreparedToSearch as e:
        error_message = (
            f"Nie przygotowano do wyszukiwania pliku {e.regulations_name}, zgłoś problem administratorowi aplikacji."
        )
        request.session[FLASH_KEY] = {"error_message": error_message}
        return RedirectResponse(url="/search/public-file", status_code=status.HTTP_303_SEE_OTHER)

    return render_page_template(request, "search_public.html", filename=filename, query=query, results=results)

from typing import Annotated

from fastapi import APIRouter, Depends, Form, Query, Request, status
from fastapi.responses import RedirectResponse

from app.application.use_cases.search import SearchFile
from app.domain.exceptions import VectorCollectionNotFound
from app.framework.dependencies.authentication import set_user_by_session_id
from app.framework.dependencies.search import get_search_file
from app.framework.web.templating import templates
from app.shared.consts import FLASH_KEY

search_router = APIRouter(tags=["search"], dependencies=(Depends(set_user_by_session_id),))


@search_router.get(
    "/files/search",
    status_code=status.HTTP_200_OK,
)
async def get_search_file_view(request: Request, filename: str = Query()):
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
        "file_search.html",
        {"request": request, "filename": filename, "error_message": error_message, "is_user_logged": is_user_logged},
    )


@search_router.post(
    "/files/search",
    status_code=status.HTTP_200_OK,
)
async def post_search_file(
    request: Request,
    search_file: Annotated[SearchFile, Depends(get_search_file)],
    query: str = Form(),
    filename: str = Query(),
):
    try:
        results = await search_file.execute()
    except VectorCollectionNotFound as e:
        error_message = f"Nie przygotowano do wyszukiwania pliku {e.collection_name}, zrób to na liście plików!"
        request.session[FLASH_KEY] = {"error_message": error_message}
        return RedirectResponse(url="/files/search", status_code=status.HTTP_303_SEE_OTHER)

    is_user_logged = request.state.user_id is not None

    return templates.TemplateResponse(
        "file_search.html",
        {
            "request": request,
            "filename": filename,
            "query": query,
            "results": results,
            "is_user_logged": is_user_logged,
        },
    )

from typing import Annotated

from fastapi import APIRouter, Depends, Form, Query, Request, status

from app.application.use_cases.search import SearchFile
from app.domain.exceptions import VectorCollectionNotFound
from app.framework.dependencies.search import get_search_file
from app.framework.web.templating import templates

search_router = APIRouter(tags=["search"])


@search_router.get(
    "/files/search",
    status_code=status.HTTP_200_OK,
)
async def get_search_file_view(request: Request, filename: str = Query()):
    return templates.TemplateResponse(
        "file_search.html",
        {
            "request": request,
            "filename": filename,
        },
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
    error_message = ""
    results = []
    try:
        results = await search_file.execute()
    except VectorCollectionNotFound as e:
        error_message = f"Nie przygotowano do wyszukiwania pliku {e.collection_name}, zrób to na liście plików!"

    return templates.TemplateResponse(
        "file_search.html",
        {"request": request, "filename": filename, "query": query, "results": results, "error_message": error_message},
    )

from fastapi import APIRouter, Request, status, Form, Query
from app.framework.web.templating import templates

search_router = APIRouter(tags=["search"])


@search_router.get(
    "/files/search",
    status_code=status.HTTP_200_OK,
)
async def get_search_file(request: Request, filename: str = Query()):
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
    query: str = Form(...),
    filename: str = Query()
):
    # TODO: Implement use case
    results = []

    return templates.TemplateResponse(
        "file_search.html",
        {
            "request": request,
            "filename": filename,
            "query": query,
            "results": results,
        },
    )

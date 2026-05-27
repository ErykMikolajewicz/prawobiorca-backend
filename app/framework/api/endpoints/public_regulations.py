from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from app.application.dtos.regulations import RegulationRepresentation
from app.application.dtos.search import SearchParams, SearchResult
from app.application.use_cases.regulations import ListRegulations, SearchRegulation
from app.domain.exceptions import RegulationsNotPreparedToSearch
from app.domain.value_objects.regulations import RegulationType
from app.framework.dependencies.regulations import get_list_regulations, get_search_regulation

public_regulations_router = APIRouter(tags=["regulations"], prefix="/api")


@public_regulations_router.get(
    "/regulations",
    responses={status.HTTP_204_NO_CONTENT: {"descriptions": "Not found public files with that criteria."}},
)
async def get_public_regulations(
    list_regulations: Annotated[ListRegulations, Depends(get_list_regulations)],
    regulation_type: RegulationType | None = Query(default=None, alias="documentType"),
) -> list[RegulationRepresentation]:
    user_id = None
    public_regulations = await list_regulations.execute(user_id, regulation_type)
    if not public_regulations:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="No public files for given search criteria.")

    return public_regulations


@public_regulations_router.get(
    "/regulations/{regulationId}/documents",
    responses={
        status.HTTP_204_NO_CONTENT: {"description": "No search results."},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"description": "Regulation not prepared, normally should not occur."},
    },
)
async def search_regulation_documents(
    search_regulation: Annotated[SearchRegulation, Depends(get_search_regulation)],
    regulation_id: Annotated[UUID, Path(alias="regulationId")],
    search_params: Annotated[SearchParams, Query()],
) -> list[SearchResult]:
    user_id = None
    try:
        results = await search_regulation.execute(user_id, regulation_id, search_params)
    except RegulationsNotPreparedToSearch as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Regulation {e.regulations_name}, not prepared to search,"
            f" report problem to application administrator.",
        )

    return results

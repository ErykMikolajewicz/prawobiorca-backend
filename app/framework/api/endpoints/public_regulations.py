from typing import Annotated

from app.application.dtos.regulations import RegulationRepresentation
from app.application.use_cases.regulations import ListRegulations
from fastapi import APIRouter, Depends, HTTPException, status

from app.application.dtos.search import SearchResult
from app.application.use_cases.regulations import SearchRegulation
from app.domain.exceptions import RegulationsNotPreparedToSearch
from app.framework.dependencies.files import get_list_public_files
from app.framework.dependencies.search import get_search_public_file

public_files_router = APIRouter(tags=["regulations"], prefix="/api")


@public_files_router.get(
    "/regulations",
    responses={status.HTTP_204_NO_CONTENT: {"descriptions": "Not found public files with that criteria."}},
)
async def get_public_files(
    list_public_files: Annotated[ListRegulations, Depends(get_list_public_files)],
) -> list[RegulationRepresentation]:
    public_files = await list_public_files.execute()
    if not public_files:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="No public files for given search criteria.")

    return public_files


@public_files_router.get(
    "/search/public-file/{fileHashStr}",
    responses={
        status.HTTP_204_NO_CONTENT: {"description": "No search results."},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"description": "Regulation not prepared, normally should not occur"},
    },
)
async def post_search_public_file(
    search_file: Annotated[SearchRegulation, Depends(get_search_public_file)]
) -> list[SearchResult]:
    try:
        results = await search_file.execute()
    except RegulationsNotPreparedToSearch as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Nie przygotowano do wyszukiwania pliku {e.regulations_name},"
            f" zgłoś problem administratorowi aplikacji.",
        )

    return results

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.application.dtos.files import FileRepresentation
from app.application.dtos.search import SearchResult
from app.application.use_cases.files import ListPublicFiles
from app.application.use_cases.search import SearchPublicFile
from app.domain.exceptions import RegulationsNotPreparedToSearch
from app.framework.dependencies.files import get_list_public_files
from app.framework.dependencies.search import get_search_public_file_v2

public_files_router = APIRouter(tags=["public_fies"], prefix="/api/v2")


@public_files_router.get("/files", responses={status.HTTP_204_NO_CONTENT: {"description": "No public files."}})
async def get_public_files(
    list_public_files: Annotated[ListPublicFiles, Depends(get_list_public_files)],
) -> list[FileRepresentation]:
    public_files = await list_public_files.execute()

    if public_files:
        return public_files
    raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)


@public_files_router.get(
    "/search/public-file/{fileHashStr}",
    responses={
        status.HTTP_204_NO_CONTENT: {"description": "No search results."},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"description": "Regulation not prepared, normally should not occur"},
    },
)
async def post_search_public_file(
    search_file: Annotated[SearchPublicFile, Depends(get_search_public_file_v2)],
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

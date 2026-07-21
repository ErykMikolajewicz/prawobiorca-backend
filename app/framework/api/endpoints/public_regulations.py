from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query, UploadFile, status

from app.application.dtos.regulations import RegulationData, RegulationRepresentation
from app.application.dtos.search import SearchParams, SearchResult
from app.application.use_cases.regulations import AddRegulation, ListRegulations, SearchRegulation
from app.domain.exceptions import RegulationsNotPreparedToSearch
from app.domain.value_objects.regulations import RegulationType
from app.framework.dependencies.authentication import require_admin
from app.framework.dependencies.regulations import get_add_regulation, get_list_regulations, get_search_regulation

public_regulations_router = APIRouter(tags=["regulations"], prefix="/api")


@public_regulations_router.get(
    "/regulations",
    responses={status.HTTP_204_NO_CONTENT: {"descriptions": "No public files for given search criteria."}},
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

    if not results:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="No search results.")

    return results


@public_regulations_router.post(
    "/regulations",
    responses={status.HTTP_201_CREATED: {"descriptions": "Added a public regulation successfully."}},
    dependencies=(Depends(require_admin),),
    status_code=status.HTTP_201_CREATED,
)
async def add_public_regulation(
    add_regulation_: Annotated[AddRegulation, Depends(get_add_regulation)],
    regulation: UploadFile,
    regulation_type: RegulationType | None = Query(default=None, alias="regulationType"),
) -> UUID:
    regulation_name = regulation.filename

    if regulation_name is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Regulation {regulation_name} is empty, can't add empty file!",
        )

    regulation_content = await regulation.read()
    regulation_data = RegulationData(name=regulation_name, file=regulation_content, regulation_type=regulation_type)

    regulation_id = await add_regulation_.execute(user_id=None, regulation_data=regulation_data)
    return regulation_id

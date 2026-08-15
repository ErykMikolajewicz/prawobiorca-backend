from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from app.application.dtos.regulations import RegulationData, RegulationRepresentation, RegulationUploadTarget
from app.application.dtos.search import SearchParams, SearchResult
from app.application.use_cases.regulations import (
    AddRegulation,
    ConfirmRegulationUpload,
    DeleteRegulation,
    GetRegulationDownloadUrl,
    ListRegulations,
    PrepareRegulation,
    SearchRegulation,
)
from app.domain.exceptions.regulations import (
    RegulationAlreadyInitialized,
    RegulationContentNotFound,
    RegulationNotFound,
    RegulationServiceUnavailable,
    RegulationsNotPreparedToSearch,
)
from app.domain.value_objects.regulations import RegulationType
from app.framework.dependencies.authentication import require_admin
from app.framework.dependencies.regulations import (
    get_add_regulation,
    get_confirm_regulation_upload,
    get_delete_regulation,
    get_list_regulations,
    get_prepare_regulation,
    get_regulation_download_url,
    get_search_regulation,
)

public_regulations_router = APIRouter(tags=["regulations"], prefix="/api")


@public_regulations_router.get(
    "/regulations",
    responses={status.HTTP_204_NO_CONTENT: {"description": "No public files for given search criteria."}},
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
        status.HTTP_400_BAD_REQUEST: {"description": "Regulation not prepared, normally should not occur."},
        status.HTTP_404_NOT_FOUND: {"description": "Regulation not found."},
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
    except RegulationNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Regulation with id {regulation_id} not found."
        )
    except RegulationsNotPreparedToSearch as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Regulation {e.regulations_name}, not prepared to search,"
            f" report problem to application administrator.",
        )

    if not results:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="No search results.")

    return results


@public_regulations_router.post(
    "/regulations",
    dependencies=(Depends(require_admin),),
    status_code=status.HTTP_201_CREATED,
)
async def add_public_regulation(
    add_regulation_: Annotated[AddRegulation, Depends(get_add_regulation)],
    regulation_data: RegulationData,
) -> RegulationUploadTarget:
    user_id = None

    return await add_regulation_.execute(user_id, regulation_data)


@public_regulations_router.post(
    "/regulations/{regulationId}/confirm-upload",
    dependencies=(Depends(require_admin),),
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Regulation not found!"},
        status.HTTP_409_CONFLICT: {"description": "Regulation already prepared or content not found on storage!"},
    },
)
async def confirm_public_regulation_upload(
    confirm_upload: Annotated[ConfirmRegulationUpload, Depends(get_confirm_regulation_upload)],
    regulation_id: Annotated[UUID, Path(alias="regulationId")],
):
    user_id = None
    try:
        await confirm_upload.execute(user_id, regulation_id)
    except RegulationNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Regulation not found!")
    except RegulationContentNotFound:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Regulation content not found in storage!",
        )
    except RegulationAlreadyInitialized:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Regulation is already prepared!",
        )


@public_regulations_router.get(
    "/regulations/{regulationId}/download-url",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Regulation not found!"},
    },
)
async def get_public_regulation_download_url(
    get_download_url: Annotated[GetRegulationDownloadUrl, Depends(get_regulation_download_url)],
    regulation_id: Annotated[UUID, Path(alias="regulationId")],
) -> str:
    user_id = None
    try:
        return await get_download_url.execute(user_id, regulation_id)
    except RegulationNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Regulation not found!")


@public_regulations_router.delete(
    "/regulations/{regulationId}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=(Depends(require_admin),),
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Regulation not found!"},
    },
)
async def delete_public_regulation(
    delete_regulation_: Annotated[DeleteRegulation, Depends(get_delete_regulation)],
    regulation_id: UUID = Path(alias="regulationId"),
):
    user_id = None
    try:
        await delete_regulation_.execute(user_id, regulation_id)
    except RegulationNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Regulation not found!")


@public_regulations_router.post(
    "/regulations/{regulationId}/preparation",
    dependencies=(Depends(require_admin),),
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Regulation to prepare not found!"},
        status.HTTP_409_CONFLICT: {"description": "Regulation already prepared, or its content not uploaded!"},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"description": "Preparation service not working!"},
    },
)
async def prepare_public_regulation(
    prepare_regulation_: Annotated[PrepareRegulation, Depends(get_prepare_regulation)],
    regulation_id: Annotated[UUID, Path(alias="regulationId")],
):
    user_id = None
    try:
        await prepare_regulation_.execute(user_id, regulation_id)
    except RegulationNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Regulation to prepare not found!",
        )
    except RegulationAlreadyInitialized:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Regulation already prepared to search!",
        )
    except RegulationContentNotFound:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Regulation content not uploaded!",
        )
    except RegulationServiceUnavailable:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Preparation service not working!",
        )

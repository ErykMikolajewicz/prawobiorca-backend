from typing import Annotated, cast
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query, UploadFile, status

from app.application.dtos.regulations import RegulationData, RegulationRepresentation
from app.application.use_cases.regulations import AddRegulation, DeleteRegulation, ListRegulations
from app.domain.value_objects.regulations import RegulationType
from app.framework.dependencies.authentication import require_logged_user, set_user_by_session_id
from app.framework.dependencies.regulations import get_add_regulation, get_delete_regulation, get_list_regulations

user_regulations_router = APIRouter(
    tags=["user_regulations"], dependencies=(Depends(set_user_by_session_id),), prefix="/api"
)


@user_regulations_router.get(
    "/user/regulations",
    responses={
        status.HTTP_204_NO_CONTENT: {"descriptions": "Not found user files with that criteria."},
    },
)
async def get_user_regulations(
    list_regulations: Annotated[ListRegulations, Depends(get_list_regulations)],
    user_id: Annotated[UUID, Depends(require_logged_user)],
    regulation_type: RegulationType | None = Query(default=None, alias="documentType"),
) -> list[RegulationRepresentation]:
    user_regulations = await list_regulations.execute(user_id, regulation_type)

    if not user_regulations:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT, detail="No user regulations for given search criteria."
        )

    return user_regulations


@user_regulations_router.post(
    "/user/regulations",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {"descriptions": "Successfully add regulation."},
    },
    dependencies=(Depends(require_logged_user),),
)
async def add_user_regulation(
    user_id: Annotated[UUID, Depends(require_logged_user)],
    add_regulation_: Annotated[AddRegulation, Depends(get_add_regulation)],
    regulation: UploadFile,
    regulation_type: RegulationType | None = Query(default=None),
) -> RegulationRepresentation:
    file_bytes = await regulation.read()
    file_name = cast(str, regulation.filename)
    try:
        regulation_data = RegulationData(name=file_name, file=file_bytes)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Plik {file_name} jest pusty, nie można dodać pustego pliku!",
        )

    regulation_representation = await add_regulation_.execute(user_id, regulation_type, regulation_data)
    return regulation_representation


@user_regulations_router.delete(
    "/user/regulations/{regulationId}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_204_NO_CONTENT: {"description": "Regulation deleted."},
        status.HTTP_404_NOT_FOUND: {"description": "Regulation not found!"},
    },
)
async def delete_user_regulation(
    user_id: Annotated[UUID, Depends(require_logged_user)],
    delete_user_regulation_: Annotated[DeleteRegulation, Depends(get_delete_regulation)],
    regulation_id: UUID = Path(alias="regulationId"),
):
    try:
        await delete_user_regulation_.execute(user_id, regulation_id)
    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Regulation not found!")

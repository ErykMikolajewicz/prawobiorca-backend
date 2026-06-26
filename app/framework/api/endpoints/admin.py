from typing import Annotated, cast
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, status

from app.application.dtos.regulations import RegulationData
from app.application.use_cases.regulations import AddRegulation
from app.domain.value_objects.regulations import RegulationType
from app.framework.dependencies.authentication import require_admin
from app.framework.dependencies.regulations import (
    get_add_regulation,
)

admin_router = APIRouter(
    tags=["admin"],
    prefix="/admin",
    dependencies=[Depends(require_admin)],
)


@admin_router.post(
    "/regulations",
    responses={status.HTTP_201_CREATED: {"descriptions": "Added a public regulation successfully."}},
)
async def add_public_regulation(
    add_regulation_: Annotated[AddRegulation, Depends(get_add_regulation)],
    regulation: UploadFile,
    regulation_type: RegulationType | None = Query(default=None, alias="documentType"),
) -> UUID:
    regulation_content = await regulation.read()
    regulation_name = cast(str, regulation.filename)

    try:
        regulation_data = RegulationData(name=regulation_name, file=regulation_content)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Regulation {regulation_name} is empty, can't add empty file!",
        )

    regulation_id = await add_regulation_.execute(
        user_id=None, regulation_type=regulation_type, regulation_data=regulation_data
    )
    return regulation_id

from typing import Annotated, cast

from app.application.dtos.files import RegulationData, RegulationRepresentation
from app.application.use_cases.user_files import (
    AddUserFile,
    DeleteUserFile,
    ListUserFiles,
)
from app.framework.dependencies.user_files import get_delete_user_file, get_list_user_files
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, status

from app.application.interfaces.regulations import RegulationsManager, RegulationsRepository
from app.application.interfaces.relational import AsyncSession
from app.domain.value_objects.regulations import RegulationType
from app.framework.dependencies.authentication import require_logged_user, set_user_by_session_id
from app.framework.dependencies.file_managment import get_user_file_manager
from app.framework.dependencies.file_storage import get_users_file_repository
from app.framework.dependencies.relational import get_relational_session

user_files_router = APIRouter(tags=["user_regulations"], dependencies=(Depends(set_user_by_session_id),), prefix="/api")


@user_files_router.get(
    "/user/regulations",
    responses={
        status.HTTP_204_NO_CONTENT: {"descriptions": "Not found user files with that criteria."},
    },
)
async def get_user_regulations(
    list_user_regulations: Annotated[ListUserFiles, Depends(get_list_user_files)],
) -> list[RegulationRepresentation]:
    user_regulations = await list_user_regulations.execute()

    if not user_regulations:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT,
                            detail="No user regulations for given search criteria.")

    return user_regulations


@user_files_router.post(
    "/user/regulations",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {"descriptions": "Successfully add regulation."},
    },
    dependencies=(Depends(require_logged_user),),
)
async def add_user_regulation(
    session: Annotated[AsyncSession, Depends(get_relational_session)],
    user_file_manager: Annotated[RegulationsManager, Depends(get_user_file_manager)],
    regulation: UploadFile,
    files_repository: Annotated[RegulationsRepository, Depends(get_users_file_repository)],
    document_type: RegulationType | None = Query(default=None),
) -> RegulationRepresentation:
    file_bytes = await regulation.read()
    file_name = cast(str, regulation.filename)
    try:
        file_data = RegulationData(name=file_name, file=file_bytes)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Plik {file_name} jest pusty, nie można dodać pustego pliku!",
        )

    add_regulation_ = AddUserFile(session, user_file_manager, file_data, files_repository, document_type)

    regulation_representation = await add_regulation_.execute()
    return regulation_representation


@user_files_router.delete(
    "/user/regulations/{regulationId}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={status.HTTP_204_NO_CONTENT: {"description": "Regulation deleted."},
               status.HTTP_404_NOT_FOUND: {"description": "Regulation not found!"}},
)
async def delete_user_regulation(
    delete_user_regulation_: Annotated[DeleteUserFile, Depends(get_delete_user_file)],
):
    try:
        await delete_user_regulation_.execute()
    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Regulation not found!")

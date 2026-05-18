from typing import Annotated

from fastapi import Depends, Form, Path, Query

from app.application.interfaces.file_managment import UserFileManager
from app.application.interfaces.file_storage import UsersFilesRepository
from app.application.interfaces.regulations import UserRegulationsRepository
from app.application.interfaces.relational import AsyncSession
from app.application.services.regulations import RegulationPreparator
from app.application.use_cases.user_files import DeleteUserFile, ListUserFiles, PrepareUserFile
from app.framework.dependencies.document_types import DocumentType
from app.framework.dependencies.file_managment import get_user_file_manager
from app.framework.dependencies.file_storage import get_users_file_repository
from app.framework.dependencies.regulations import get_regulation_preparator, get_user_regulations_repository
from app.framework.dependencies.relational import get_relational_session


def get_prepare_user_file(
    session: Annotated[AsyncSession, Depends(get_relational_session)],
    file_hash_str: Annotated[str, Form(..., alias="fileHashStr")],
    regulation_preparator: Annotated[RegulationPreparator, Depends(get_regulation_preparator)],
    files_repository: Annotated[UsersFilesRepository, Depends(get_users_file_repository)],
    regulations_repository: Annotated[UserRegulationsRepository, Depends(get_user_regulations_repository)],
    user_file_manager: Annotated[UserFileManager, Depends(get_user_file_manager)],
) -> PrepareUserFile:

    return PrepareUserFile(
        session=session,
        files_repository=files_repository,
        regulations_repository=regulations_repository,
        file_hash_str=file_hash_str,
        user_file_manager=user_file_manager,
        regulation_preparator=regulation_preparator,
    )


def get_list_user_files(
    session: Annotated[AsyncSession, Depends(get_relational_session)],
    user_file_manager: Annotated[UserFileManager, Depends(get_user_file_manager)],
    document_type: DocumentType | None = Query(default=None, alias="documentType"),
) -> ListUserFiles:
    return ListUserFiles(session, user_file_manager, document_type)


def get_delete_user_file(
    file_hash_string: Annotated[str, Path(..., alias="fileHashString")],
    session: Annotated[AsyncSession, Depends(get_relational_session)],
    user_file_manager: Annotated[UserFileManager, Depends(get_user_file_manager)],
    regulations_repository: Annotated[UserRegulationsRepository, Depends(get_user_regulations_repository)],
) -> DeleteUserFile:
    return DeleteUserFile(
        session=session,
        file_manager=user_file_manager,
        regulations_repository=regulations_repository,
        file_hash_str=file_hash_string,
    )

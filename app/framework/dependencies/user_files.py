from typing import Annotated

from fastapi import Depends, Path

from app.application.interfaces.file_storage import UsersFilesRepository
from app.application.services.embedding import DocumentEmbedder
from app.application.use_cases.user_files import ListUserFiles, PrepareUserFile
from app.framework.dependencies.embeddings import get_document_embedder
from app.framework.dependencies.file_storage import get_users_file_repository
from app.framework.dependencies.regulations import get_regulations_repository


def get_prepare_user_file(
    file_name: Annotated[str, Path(..., alias="fileName")],
    document_embedder: Annotated[DocumentEmbedder, Depends(get_document_embedder)],
    files_repository: Annotated[UsersFilesRepository, Depends(get_users_file_repository)],
) -> PrepareUserFile:
    regulations_repository = get_regulations_repository(filename=file_name)

    return PrepareUserFile(
        document_embedder=document_embedder,
        files_repository=files_repository,
        regulations_repository=regulations_repository,
        file_name=file_name,
    )


def get_list_user_files(
    files_repository: Annotated[UsersFilesRepository, Depends(get_users_file_repository)],
) -> ListUserFiles:
    return ListUserFiles(files_repository)

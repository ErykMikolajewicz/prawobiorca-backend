from typing import Annotated

from fastapi import Depends, Path

from app.application.interfaces.file_storage import StorageRepository
from app.application.ports.embeddings import EmbeddingPort
from app.application.use_cases.user_files import PrepareUserFile
from app.framework.dependencies.embeddings import get_embeddings_port
from app.framework.dependencies.file_storage import get_file_storage
from app.framework.dependencies.regulations import get_regulations_repository


def get_prepare_user_file(
    file_name: Annotated[str, Path(..., alias="fileName")],
    embedding_port: Annotated[EmbeddingPort, Depends(get_embeddings_port)],
    storage_repository: Annotated[StorageRepository, Depends(get_file_storage)],
) -> PrepareUserFile:
    regulations_repository = get_regulations_repository(filename=file_name)

    return PrepareUserFile(
        embedding_port=embedding_port,
        storage_repository=storage_repository,
        regulations_repository=regulations_repository,
        file_name=file_name,
    )

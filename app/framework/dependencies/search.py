from typing import Annotated

from fastapi import Depends, Form

from app.application.interfaces.regulations import PublicRegulationsRepository, UserRegulationsRepository
from app.application.ports.texts import TextsEmbedder
from app.application.use_cases.search import SearchPublicFile, SearchUserFile
from app.framework.dependencies.embeddings import get_embeddings_port
from app.framework.dependencies.regulations import get_public_regulations_repository, get_user_regulations_repository


def get_search_user_file(
    query: Annotated[str, Form()],
    embedding_port: Annotated[TextsEmbedder, Depends(get_embeddings_port)],
    file_hash_str: Annotated[str, Form(alias="fileHashStr")],
    regulations_repository: Annotated[UserRegulationsRepository, Depends(get_user_regulations_repository)],
) -> SearchUserFile:
    return SearchUserFile(embedding_port, regulations_repository, query, file_hash_str)


def get_search_public_file(
    query: Annotated[str, Form()],
    embedding_port: Annotated[TextsEmbedder, Depends(get_embeddings_port)],
    file_hash_str: Annotated[str, Form(alias="fileHashStr")],
    regulations_repository: Annotated[PublicRegulationsRepository, Depends(get_public_regulations_repository)],
) -> SearchPublicFile:
    return SearchPublicFile(embedding_port, regulations_repository, query, file_hash_str)

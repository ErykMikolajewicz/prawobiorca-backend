from typing import Annotated

from fastapi import Depends, Form, Query

from app.application.interfaces.regulations import PublicRegulationsRepository, UserRegulationsRepository
from app.application.ports.texts import TextsEmbedder
from app.application.use_cases.search import SearchPublicFile, SearchUserFile
from app.framework.dependencies.regulations import get_public_regulations_repository, get_user_regulations_repository
from app.framework.dependencies.text_transformation import get_texts_embedder


def get_search_user_file(
    query: Annotated[str, Form()],
    texts_embedder: Annotated[TextsEmbedder, Depends(get_texts_embedder)],
    file_hash_str: Annotated[str, Form(alias="fileHashStr")],
    regulations_repository: Annotated[UserRegulationsRepository, Depends(get_user_regulations_repository)],
) -> SearchUserFile:
    return SearchUserFile(texts_embedder, regulations_repository, query, file_hash_str)


def get_search_public_file(
    query: Annotated[str, Form()],
    texts_embedder: Annotated[TextsEmbedder, Depends(get_texts_embedder)],
    file_hash_str: Annotated[str, Form(alias="fileHashStr")],
    regulations_repository: Annotated[PublicRegulationsRepository, Depends(get_public_regulations_repository)],
) -> SearchPublicFile:
    return SearchPublicFile(texts_embedder, regulations_repository, query, file_hash_str)


def get_search_public_file_v2(
    query: Annotated[str, Query()],
    texts_embedder: Annotated[TextsEmbedder, Depends(get_texts_embedder)],
    file_hash_str: Annotated[str, Query(alias="fileHashStr")],
    regulations_repository: Annotated[PublicRegulationsRepository, Depends(get_public_regulations_repository)],
) -> SearchPublicFile:
    return SearchPublicFile(texts_embedder, regulations_repository, query, file_hash_str)

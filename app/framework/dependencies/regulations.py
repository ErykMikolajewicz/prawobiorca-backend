from typing import Annotated, Any

from fastapi import Depends, Request

from app.application.interfaces.documents import DocumentsRepository
from app.application.interfaces.regulations import RegulationsRepository, RegulationsStorage
from app.application.interfaces.relational import SessionMaker
from app.application.ports.regulations import RegulationSpliter
from app.application.ports.texts import TextsEmbedder
from app.application.services.embedding import DocumentEmbedder
from app.application.services.regulations import RegulationPreparator
from app.application.use_cases.regulations import (
    AddRegulation,
    ConfirmRegulationUpload,
    DeleteRegulation,
    GetRegulationDownloadUrl,
    ListRegulations,
    PrepareRegulation,
    SearchRegulation,
)
from app.framework.dependencies.relational import get_session_maker
from app.framework.dependencies.text_transformation import (
    get_document_embedder,
    get_regulations_splitter,
    get_texts_embedder,
)
from app.infrastructure.relational_db.repositories.documents import RegulationsDocumentsRepository
from app.infrastructure.relational_db.repositories.regulations import RegulationsManagerRepository


def get_documents_repository() -> DocumentsRepository:
    return RegulationsDocumentsRepository()


def get_file_storage_client(request: Request) -> Any:
    return request.app.state.file_storage_client


def get_regulations_storage(client: Annotated[Any, Depends(get_file_storage_client)]) -> RegulationsStorage:
    from app.infrastructure.object_storage.on_premise.repository import S3RegulationsStorage

    return S3RegulationsStorage(client)


def get_regulation_repository() -> RegulationsRepository:
    return RegulationsManagerRepository()


def get_regulation_preparator(
    document_embedder: Annotated[DocumentEmbedder, Depends(get_document_embedder)],
    regulations_splitter: Annotated[RegulationSpliter, Depends(get_regulations_splitter)],
) -> RegulationPreparator:
    return RegulationPreparator(regulations_splitter, document_embedder)


def get_list_regulations(
    session_maker: Annotated[SessionMaker, Depends(get_session_maker)],
    regulation_manager: Annotated[RegulationsRepository, Depends(get_regulation_repository)],
) -> ListRegulations:

    return ListRegulations(session_maker, regulation_manager)


def get_prepare_regulation(
    session_maker: Annotated[SessionMaker, Depends(get_session_maker)],
    regulations_storage: Annotated[RegulationsStorage, Depends(get_regulations_storage)],
    documents_repository: Annotated[DocumentsRepository, Depends(get_documents_repository)],
    regulations_repository: Annotated[RegulationsRepository, Depends(get_regulation_repository)],
    regulation_preparator: Annotated[RegulationPreparator, Depends(get_regulation_preparator)],
) -> PrepareRegulation:

    return PrepareRegulation(
        session_maker,
        regulations_storage,
        documents_repository,
        regulations_repository,
        regulation_preparator,
    )


def get_delete_regulation(
    session_maker: Annotated[SessionMaker, Depends(get_session_maker)],
    regulations_repository: Annotated[RegulationsRepository, Depends(get_regulation_repository)],
    documents_repository: Annotated[DocumentsRepository, Depends(get_documents_repository)],
    regulations_storage: Annotated[RegulationsStorage, Depends(get_regulations_storage)],
) -> DeleteRegulation:
    return DeleteRegulation(session_maker, regulations_repository, documents_repository, regulations_storage)


def get_search_regulation(
    session_maker: Annotated[SessionMaker, Depends(get_session_maker)],
    texts_embedder: Annotated[TextsEmbedder, Depends(get_texts_embedder)],
    documents_repository: Annotated[DocumentsRepository, Depends(get_documents_repository)],
    regulations_repository: Annotated[RegulationsRepository, Depends(get_regulation_repository)],
) -> SearchRegulation:
    return SearchRegulation(session_maker, texts_embedder, documents_repository, regulations_repository)


def get_add_regulation(
    session_maker: Annotated[SessionMaker, Depends(get_session_maker)],
    regulations_repository: Annotated[RegulationsRepository, Depends(get_regulation_repository)],
    regulations_storage: Annotated[RegulationsStorage, Depends(get_regulations_storage)],
) -> AddRegulation:
    return AddRegulation(session_maker, regulations_repository, regulations_storage)


def get_confirm_regulation_upload(
    session_maker: Annotated[SessionMaker, Depends(get_session_maker)],
    regulations_repository: Annotated[RegulationsRepository, Depends(get_regulation_repository)],
    regulations_storage: Annotated[RegulationsStorage, Depends(get_regulations_storage)],
) -> ConfirmRegulationUpload:
    return ConfirmRegulationUpload(session_maker, regulations_repository, regulations_storage)


def get_regulation_download_url(
    session_maker: Annotated[SessionMaker, Depends(get_session_maker)],
    regulations_repository: Annotated[RegulationsRepository, Depends(get_regulation_repository)],
    regulations_storage: Annotated[RegulationsStorage, Depends(get_regulations_storage)],
) -> GetRegulationDownloadUrl:
    return GetRegulationDownloadUrl(session_maker, regulations_repository, regulations_storage)

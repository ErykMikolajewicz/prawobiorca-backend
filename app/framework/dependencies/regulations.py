from typing import Annotated

from fastapi import Depends

from app.application.interfaces.documents import DocumentsRepository
from app.application.interfaces.regulations import RegulationsManager, RegulationsRepository
from app.application.interfaces.relational import SessionMaker
from app.application.ports.regulations import RegulationSpliter
from app.application.ports.texts import TextsEmbedder
from app.application.services.embedding import DocumentEmbedder
from app.application.services.regulations import RegulationPreparator
from app.application.use_cases.regulations import (
    AddRegulation,
    DeleteRegulation,
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


def get_regulations_repository() -> RegulationsRepository:
    from app.infrastructure.local_storage.repository import LocalRegulationsStorage

    return LocalRegulationsStorage()


def get_regulation_manager() -> RegulationsManager:
    return RegulationsManagerRepository()


def get_regulation_preparator(
    document_embedder: Annotated[DocumentEmbedder, Depends(get_document_embedder)],
    regulations_splitter: Annotated[RegulationSpliter, Depends(get_regulations_splitter)],
) -> RegulationPreparator:
    return RegulationPreparator(regulations_splitter, document_embedder)


def get_list_regulations(
    session_maker: Annotated[SessionMaker, Depends(get_session_maker)],
    regulation_manager: Annotated[RegulationsManager, Depends(get_regulation_manager)],
) -> ListRegulations:

    return ListRegulations(session_maker, regulation_manager)


def get_prepare_regulation(
    session_maker: Annotated[SessionMaker, Depends(get_session_maker)],
    regulations_repository: Annotated[RegulationsRepository, Depends(get_regulations_repository)],
    documents_repository: Annotated[DocumentsRepository, Depends(get_documents_repository)],
    regulations_manager: Annotated[RegulationsManager, Depends(get_regulation_manager)],
    regulation_preparator: Annotated[RegulationPreparator, Depends(get_regulation_preparator)],
) -> PrepareRegulation:

    return PrepareRegulation(
        session_maker,
        regulations_repository,
        documents_repository,
        regulations_manager,
        regulation_preparator,
    )


def get_delete_regulation(
    session_maker: Annotated[SessionMaker, Depends(get_session_maker)],
    regulations_manager: Annotated[RegulationsManager, Depends(get_regulation_manager)],
    documents_repository: Annotated[DocumentsRepository, Depends(get_documents_repository)],
    regulations_repository: Annotated[RegulationsRepository, Depends(get_regulations_repository)],
) -> DeleteRegulation:
    return DeleteRegulation(session_maker, regulations_manager, documents_repository, regulations_repository)


def get_search_regulation(
    session_maker: Annotated[SessionMaker, Depends(get_session_maker)],
    texts_embedder: Annotated[TextsEmbedder, Depends(get_texts_embedder)],
    documents_repository: Annotated[DocumentsRepository, Depends(get_documents_repository)],
) -> SearchRegulation:
    return SearchRegulation(session_maker, texts_embedder, documents_repository)


def get_add_regulation(
    session_maker: Annotated[SessionMaker, Depends(get_session_maker)],
    regulations_manager: Annotated[RegulationsManager, Depends(get_regulation_manager)],
    regulations_repository: Annotated[RegulationsRepository, Depends(get_regulations_repository)],
) -> AddRegulation:
    return AddRegulation(session_maker, regulations_manager, regulations_repository)

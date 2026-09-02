from typing import Annotated, Any

from fastapi import Depends, Request

from app.application.interfaces.documents import DocumentsRepository
from app.application.interfaces.regulations import RegulationsRepository, RegulationsStorage
from app.application.interfaces.relational import SessionMaker
from app.application.ports.tasks import RegulationPreparationScheduler
from app.application.ports.texts import TextsEmbedder
from app.application.use_cases.regulations import (
    AddRegulation,
    ConfirmRegulationUpload,
    DeleteRegulation,
    GetRegulationDownloadUrl,
    ListRegulations,
    RetryRegulationPreparation,
    SearchRegulation,
)
from app.framework.dependencies.ai_services import get_texts_embedder
from app.framework.dependencies.relational import get_session_maker
from app.infrastructure.object_storage.repository import S3RegulationsStorage
from app.infrastructure.relational_db.repositories.documents import RegulationsDocumentsRepository
from app.infrastructure.relational_db.repositories.regulations import RegulationsManagerRepository
from app.infrastructure.tasks.regulations import TaskiqRegulationPreparationScheduler


def get_documents_repository() -> DocumentsRepository:
    return RegulationsDocumentsRepository()


def get_file_storage_client(request: Request) -> Any:
    return request.app.state.file_storage_client


def get_file_storage_presign_client(request: Request) -> Any:
    return request.app.state.file_storage_presign_client


def get_regulations_storage(
    client: Annotated[Any, Depends(get_file_storage_client)],
    presign_client: Annotated[Any, Depends(get_file_storage_presign_client)],
) -> RegulationsStorage:
    return S3RegulationsStorage(client, presign_client)


def get_regulation_repository() -> RegulationsRepository:
    return RegulationsManagerRepository()


def get_broker(request: Request) -> Any:
    return request.app.state.broker


def get_regulations_preparation_scheduler(
    broker: Annotated[Any, Depends(get_broker)],
) -> RegulationPreparationScheduler:
    return TaskiqRegulationPreparationScheduler(broker)


def get_list_regulations(
    session_maker: Annotated[SessionMaker, Depends(get_session_maker)],
    regulation_manager: Annotated[RegulationsRepository, Depends(get_regulation_repository)],
) -> ListRegulations:

    return ListRegulations(session_maker, regulation_manager)


def get_retry_regulation_preparation(
    session_maker: Annotated[SessionMaker, Depends(get_session_maker)],
    regulations_repository: Annotated[RegulationsRepository, Depends(get_regulation_repository)],
    regulation_preparation_scheduler: Annotated[
        RegulationPreparationScheduler, Depends(get_regulations_preparation_scheduler)
    ],
) -> RetryRegulationPreparation:
    return RetryRegulationPreparation(session_maker, regulations_repository, regulation_preparation_scheduler)


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
    regulation_preparation_scheduler: Annotated[
        RegulationPreparationScheduler, Depends(get_regulations_preparation_scheduler)
    ],
) -> ConfirmRegulationUpload:
    return ConfirmRegulationUpload(
        session_maker, regulations_repository, regulations_storage, regulation_preparation_scheduler
    )


def get_regulation_download_url(
    session_maker: Annotated[SessionMaker, Depends(get_session_maker)],
    regulations_repository: Annotated[RegulationsRepository, Depends(get_regulation_repository)],
    regulations_storage: Annotated[RegulationsStorage, Depends(get_regulations_storage)],
) -> GetRegulationDownloadUrl:
    return GetRegulationDownloadUrl(session_maker, regulations_repository, regulations_storage)

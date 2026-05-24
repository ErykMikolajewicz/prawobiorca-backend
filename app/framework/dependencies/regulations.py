from typing import Annotated

from app.application.ports.reguations import RegulationSpliter
from fastapi import Depends, Request

from app.application.interfaces.documents import DocumentsRepository
from app.application.interfaces.regulations import PublicRegulationsRepository
from app.application.services.embedding import DocumentEmbedder
from app.application.services.regulations import RegulationPreparator
from app.framework.dependencies.text_transformation import get_document_embedder, get_regulations_splitter
from app.shared.settings.application import VectorDBType, app_settings


def get_user_regulations_repository(request: Request) -> DocumentsRepository:
    match app_settings.VECTOR_DB:
        case VectorDBType.QDRANT:
            from app.infrastructure.qdrant_db.connection import qdrant_client
            from app.infrastructure.qdrant_db.repository import QdrantUserRegulationsRepository

            user_id = request.state.user_id

            return QdrantUserRegulationsRepository(qdrant_client, user_id)
        case _:
            raise Exception(f"Invalid vector db configuration {app_settings.VECTOR_DB} !")


def get_public_regulations_repository() -> PublicRegulationsRepository:
    match app_settings.VECTOR_DB:
        case VectorDBType.QDRANT:
            from app.infrastructure.qdrant_db.connection import qdrant_client
            from app.infrastructure.qdrant_db.repository import QdrantPublicRegulationsRepository

            return QdrantPublicRegulationsRepository(qdrant_client)
        case _:
            raise Exception(f"Invalid vector db configuration {app_settings.VECTOR_DB} !")


def get_regulation_preparator(
    document_embedder: Annotated[DocumentEmbedder, Depends(get_document_embedder)],
    regulations_splitter: Annotated[RegulationSpliter, Depends(get_regulations_splitter)],
) -> RegulationPreparator:
    return RegulationPreparator(regulations_splitter, document_embedder)

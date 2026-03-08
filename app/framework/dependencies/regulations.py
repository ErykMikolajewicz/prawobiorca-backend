from fastapi import Request

from app.application.interfaces.regulations import UserRegulationsRepository
from app.shared.settings.application import VectorDBType, app_settings


def get_regulations_repository(request: Request) -> UserRegulationsRepository:
    match app_settings.VECTOR_DB:
        case VectorDBType.QDRANT:
            from app.infrastructure.qdrant_db.connection import qdrant_client
            from app.infrastructure.qdrant_db.repository import QdrantUserRegulationsRepository

            user_id = request.state.user_id

            return QdrantUserRegulationsRepository(qdrant_client, user_id)
        case _:
            raise Exception(f"Invalid vector db configuration {app_settings.VECTOR_DB} !")

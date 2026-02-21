from fastapi import Query

from app.application.interfaces.regulations import RegulationsRepository
from app.shared.settings.application import VectorDBType, app_settings


def get_regulations_repository(filename: str = Query()) -> RegulationsRepository:
    match app_settings.VECTOR_DB:
        case VectorDBType.QDRANT:
            from app.infrastructure.qdrant_db.connection import qdrant_client
            from app.infrastructure.qdrant_db.repository import QdrantRegulationsRepository

            return QdrantRegulationsRepository(
                client=qdrant_client,
                collection_name=filename,
            )
        case _:
            raise Exception(f"Invalid vector db configuration {app_settings.VECTOR_DB} !")

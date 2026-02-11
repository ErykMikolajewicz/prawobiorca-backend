from typing import Annotated

from fastapi import Depends, Query
from qdrant_client import AsyncQdrantClient

from app.domain.interfaces.vector_db import VectorDBRepository
from app.infrastructure.enums import VectorDBType
from app.infrastructure.vector_db.qdrant.qdrant_db import get_qdrant_client
from app.infrastructure.vector_db.qdrant.repository import QdrantRepository
from app.shared.settings.application import app_settings


def get_vector_db_repository(
    qdrant_client: Annotated[AsyncQdrantClient, Depends(get_qdrant_client)],
    filename: str = Query()
) -> VectorDBRepository:
    match app_settings.VECTOR_DB:
        case VectorDBType.QDRANT:
            return QdrantRepository(
                client=qdrant_client,
                collection_name=filename,
            )
        case _:
            raise Exception(f"Invalid vector db configuration {app_settings.VECTOR_DB} !")

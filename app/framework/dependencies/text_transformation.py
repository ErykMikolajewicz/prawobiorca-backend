from typing import Annotated

from fastapi import Depends, Request
from httpx import AsyncClient

import app.infrastructure.text_transformator.regulation_splitter as rs
import app.infrastructure.text_transformator.text_embedder as te
from app.application.ports.reguations import RegulationSpliter
from app.application.ports.texts import TextsEmbedder
from app.application.services.embedding import DocumentEmbedder
from app.shared.settings.text_transformator import text_transformator_settings


def get_text_transformation_client(request: Request) -> AsyncClient:
    return request.app.state.embedding_client


def get_texts_embedder(
    client: Annotated[AsyncClient, Depends(get_text_transformation_client)],
) -> TextsEmbedder:
    return te.TextsEmbedder(client=client, texts_transformator_url=text_transformator_settings.URL)


def get_document_embedder(texts_embedder: Annotated[TextsEmbedder, Depends(get_texts_embedder)]):
    return DocumentEmbedder(texts_embedder)


def get_regulations_splitter(
    client: Annotated[AsyncClient, Depends(get_text_transformation_client)],
) -> RegulationSpliter:
    return rs.RegulationSplitter(client=client, texts_transformator_url=text_transformator_settings.URL)

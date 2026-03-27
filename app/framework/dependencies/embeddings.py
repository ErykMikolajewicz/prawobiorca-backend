from typing import Annotated

from fastapi import Depends, Request
from httpx import AsyncClient

import app.infrastructure.text_transformator.text_embedder as te
from app.application.ports.texts import TextsEmbedder
from app.application.services.embedding import DocumentEmbedder
from app.shared.settings.embeddings import text_transformator_settings


def get_embedding_client(request: Request) -> AsyncClient:
    return request.app.state.embedding_client


def get_embeddings_port(
    client: Annotated[AsyncClient, Depends(get_embedding_client)],
) -> TextsEmbedder:
    return te.TextsEmbedder(client=client, texts_transformator_url=text_transformator_settings.URL)


def get_document_embedder(embedding_port: Annotated[TextsEmbedder, Depends(get_embeddings_port)]):
    return DocumentEmbedder(embedding_port)

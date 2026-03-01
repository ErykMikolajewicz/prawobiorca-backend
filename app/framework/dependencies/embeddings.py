from typing import Annotated

from fastapi import Depends, Request
from httpx import AsyncClient

from app.application.ports.embeddings import EmbeddingPort
from app.application.services.embedding import DocumentEmbedder
from app.infrastructure.embeddings.httpx_client.port import HttpxEmbeddingsPort
from app.shared.settings.embeddings import embeddings_settings


def get_embedding_client(request: Request) -> AsyncClient:
    return request.app.state.embedding_client


def get_embeddings_port(
    client: Annotated[AsyncClient, Depends(get_embedding_client)],
) -> EmbeddingPort:
    return HttpxEmbeddingsPort(client=client, embedding_url=embeddings_settings.URL)


def get_document_embedder(embedding_port: Annotated[EmbeddingPort, Depends(get_embeddings_port)]):
    return DocumentEmbedder(embedding_port)

from typing import Annotated

from fastapi import Depends, Request
from httpx import AsyncClient

from app.domain.ports.embeddings import EmbeddingPort
from app.infrastructure.embeddings.httpx_client.port import HttpxEmbeddingsPort
from app.shared.settings.embeddings import embeddings_settings


def get_embedding_client(request: Request) -> AsyncClient:
    return request.app.state.embedding_client


def get_embeddings_port(
    client: Annotated[AsyncClient, Depends(get_embedding_client)],
) -> EmbeddingPort:
    return HttpxEmbeddingsPort(client=client, embedding_url=embeddings_settings.URL)

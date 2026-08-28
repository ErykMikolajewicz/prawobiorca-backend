from typing import Annotated

from fastapi import Depends, Request
from httpx2 import AsyncClient

import app.infrastructure.ai_services.text_embedder as te
from app.application.ports.texts import TextsEmbedder
from app.shared.settings.ai_services import embedding_service_settings


def get_ai_services_client(request: Request) -> AsyncClient:
    return request.app.state.ai_services_client


def get_texts_embedder(
    client: Annotated[AsyncClient, Depends(get_ai_services_client)],
) -> TextsEmbedder:
    return te.TextsEmbedder(client=client, embedding_service_url=embedding_service_settings.URL)

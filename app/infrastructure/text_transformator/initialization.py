from typing import Any, Awaitable, Callable

from app.shared.settings.application import HttpClientType, app_settings


async def init_text_transformator_client() -> tuple[Any, Callable[..., Awaitable[None]]]:
    match app_settings.HTTP_CLIENT:
        case HttpClientType.HTTPX:
            from app.infrastructure.text_transformator.httpx_client.connection import client

            return client, client.aclose
        case _:
            raise Exception(f"Invalid httpx client configuration {app_settings.HTTP_CLIENT} !")

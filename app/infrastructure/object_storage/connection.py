from contextlib import AsyncExitStack
from typing import Any, Awaitable, Callable

from aiobotocore.config import AioConfig
from aiobotocore.session import get_session

from app.shared.settings.object_storage import object_storage_settings

session = get_session()
exit_stack = AsyncExitStack()


async def init_object_storage_client() -> tuple[Any, Callable[..., Awaitable[None]]]:
    client = await exit_stack.enter_async_context(
        session.create_client(
            "s3",
            endpoint_url=object_storage_settings.ENDPOINT_URL,
            region_name=object_storage_settings.REGION,
            aws_access_key_id=object_storage_settings.ACCESS_KEY,
            aws_secret_access_key=object_storage_settings.SECRET_KEY,
            config=AioConfig(signature_version="s3v4"),
        )
    )
    await client.head_bucket(Bucket=object_storage_settings.BUCKET)

    return client, exit_stack.aclose

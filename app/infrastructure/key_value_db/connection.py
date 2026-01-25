from typing import Callable, Awaitable

import redis.asyncio as redis

from app.infrastructure.key_value_db.redis_db import redis_pool


async def check_key_value_db_connection() -> Callable[..., Awaitable[None]]:
    redis_client = redis.Redis(connection_pool=redis_pool)
    pong = await redis_client.ping()
    if not pong:
        raise RuntimeError("Can not connect to redis db!")
    await redis_client.aclose()
    return redis_pool.disconnect

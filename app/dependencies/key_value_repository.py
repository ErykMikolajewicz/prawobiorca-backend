from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis

from app.infrastructure.key_value_db.connection import get_redis


def get_key_value_repository(redis_client: Annotated[Redis, Depends(get_redis)]) -> Redis:
    return redis_client

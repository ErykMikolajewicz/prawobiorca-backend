from typing import Annotated

from redis.asyncio import Redis
from fastapi import Depends

from app.infrastructure.key_value_db.repository import RedisKeyValueRepository
from app.infrastructure.key_value_db.connection import get_redis


def get_key_value_repository(redis_client: Annotated[Redis, Depends(get_redis)]) -> RedisKeyValueRepository:
    return RedisKeyValueRepository(redis_client)

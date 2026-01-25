from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis

from app.infrastructure.key_value_db.redis_db import get_redis


def get_key_value_repository(key_value_repository: Annotated[Redis, Depends(get_redis)]) -> Redis:
    return key_value_repository

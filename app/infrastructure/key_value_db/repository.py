from typing import Any, AsyncContextManager

import redis.asyncio as redis

from app.domain.interfaces.key_value_db import KeyValueRepository, AbstractPipeline


class RedisPipeline(AbstractPipeline):
    def __init__(self, pipe):
        self._pipe = pipe

    async def __aenter__(self):
        await self._pipe.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._pipe.__aexit__(exc_type, exc_val, exc_tb)

    async def delete(self, key: str) -> None:
        await self._pipe.delete(key)

    async def set(self, key: str, value: Any, expire: int | None = None) -> None:
        await self._pipe.set(key, value, ex=expire)

    async def execute(self) -> None:
        await self._pipe.execute()


class RedisKeyValueRepository(KeyValueRepository):
    def __init__(self, redis_client: redis.Redis):
        self._redis = redis_client

    async def set(self, key: str, value: Any, expire: int | None = None) -> None:
        await self._redis.set(key, value, ex=expire)

    async def get(self, key: str) -> Any | None:
        return await self._redis.get(key)

    async def delete(self, key: str) -> None:
        await self._redis.delete(key)

    def pipeline(self) -> AsyncContextManager[AbstractPipeline]:
        pipe = self._redis.pipeline()
        return RedisPipeline(pipe)

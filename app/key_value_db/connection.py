import redis.asyncio as redis

from app.config import settings


redis_pool = redis.ConnectionPool(
    host=settings.key_value_db.HOST,
    port=settings.key_value_db.PORT,
    db=settings.key_value_db.DB_NUMBER,
    max_connections=settings.key_value_db.MAX_CONNECTIONS,
    decode_responses=True
)


async def get_redis() -> redis.Redis:
    redis_client = redis.Redis(connection_pool=redis_pool)
    try:
        yield redis_client  # bad type hint from PyCharm
    finally:
        await redis_client.close()


async def check_redis_connection():
    redis_client = redis.Redis(connection_pool=redis_pool)
    pong = await redis_client.ping()
    if not pong:
        raise RuntimeError("Can not connect to redis db!")
    await redis_client.close()

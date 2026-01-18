import redis.asyncio as redis

from app.shared.settings.key_value_database import redis_settings

redis_pool = redis.ConnectionPool(
    host=redis_settings.HOST,
    port=redis_settings.PORT,
    db=redis_settings.DB_NUMBER,
    max_connections=redis_settings.MAX_CONNECTIONS,
    decode_responses=True,
)


async def get_redis() -> redis.Redis:
    redis_client = redis.Redis(connection_pool=redis_pool)
    try:
        yield redis_client  # bad type hint from PyCharm
    finally:
        await redis_client.aclose()


async def check_redis_connection():
    redis_client = redis.Redis(connection_pool=redis_pool)
    pong = await redis_client.ping()
    if not pong:
        raise RuntimeError("Can not connect to redis db!")
    await redis_client.aclose()

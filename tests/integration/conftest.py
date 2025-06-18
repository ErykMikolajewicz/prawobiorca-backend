import pytest
from redis import ConnectionPool as SyncRedisPool
from redis import Redis as SyncRedis
from redis.asyncio import ConnectionPool, Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer

import alembic.command
import alembic.config
from app.dependencies.key_value_repository import get_key_value_repository
from app.infrastructure.relational_db.connection import get_relational_session
from app.main import app

REDIS_IMAGE_VERSION = "redis:8.0"
POSTGRES_IMAGE_VERSION = "postgres:17.5"


@pytest.fixture(scope="session", autouse=True)
def run_migrations(postgres_container):
    alembic_cfg = alembic.config.Config("alembic.ini")
    db_url = postgres_container.get_connection_url()
    alembic_cfg.set_main_option("sqlalchemy.url", db_url)
    alembic.command.upgrade(alembic_cfg, "head")


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer(POSTGRES_IMAGE_VERSION, driver="psycopg") as postgres:
        yield postgres


@pytest.fixture
async def override_get_relational_session(postgres_container):
    url = postgres_container.get_connection_url().replace("psycopg", "asyncpg")
    db_engine = create_async_engine(url, future=True, echo=False)
    async_session_maker = async_sessionmaker(db_engine, expire_on_commit=False, class_=AsyncSession)
    session = async_session_maker()

    async with session.begin():

        async def _override():
            yield session

        app.dependency_overrides[get_relational_session] = _override
        yield
        await session.rollback()
        await db_engine.dispose()
        app.dependency_overrides = {}


@pytest.fixture
async def db_session_maker(postgres_container):
    url = postgres_container.get_connection_url().replace("psycopg", "asyncpg")
    db_engine = create_async_engine(url, future=True, echo=False)
    async_session_maker = async_sessionmaker(db_engine, expire_on_commit=False, class_=AsyncSession)

    try:
        yield async_session_maker
    finally:
        await db_engine.dispose()


@pytest.fixture(scope="session")
def redis_container():
    with RedisContainer(REDIS_IMAGE_VERSION) as redis:
        yield redis


@pytest.fixture
async def override_get_key_value_repository(redis_container):
    redis_pool = ConnectionPool(
        host=redis_container.get_container_host_ip(),
        port=redis_container.get_exposed_port(6379),
        decode_responses=True,
    )
    redis_client = Redis(connection_pool=redis_pool)

    async def _override():
        return redis_client

    app.dependency_overrides[get_key_value_repository] = _override
    yield
    await redis_client.aclose()
    app.dependency_overrides = {}


@pytest.fixture(scope="session")
def redis_client(redis_container):
    redis_pool = SyncRedisPool(
        host=redis_container.get_container_host_ip(),
        port=redis_container.get_exposed_port(6379),
        decode_responses=True,
    )
    redis_client = SyncRedis(connection_pool=redis_pool)
    try:
        yield redis_client
    finally:
        redis_client.close()

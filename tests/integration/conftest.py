import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer
from redis.asyncio import Redis, ConnectionPool

import alembic.command
import alembic.config

from app.infrastructure.relational_db.connection import get_relational_session
from app.dependencies.key_value_repository import get_key_value_repository
from app.main import app


@pytest.fixture(scope="session", autouse=True)
def run_migrations(postgres_container):
    alembic_cfg = alembic.config.Config("alembic.ini")
    db_url = postgres_container.get_connection_url().replace("psycopg2", "psycopg")
    alembic_cfg.set_main_option("sqlalchemy.url", db_url)
    alembic.command.upgrade(alembic_cfg, "head")


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:17") as postgres:
        yield postgres


@pytest.fixture(scope="session")
async def db_engine(postgres_container):
    url = postgres_container.get_connection_url().replace("psycopg2", "asyncpg")
    engine = create_async_engine(url, future=True, echo=False)
    yield engine
    await engine.dispose()


@pytest.fixture
async def db_session(db_engine):
    async_session_maker = async_sessionmaker(db_engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session_maker() as session:
        async with session.begin():
            yield session
            await session.rollback()


@pytest.fixture
async def override_get_relational_session(db_session):
    async def _get():
        yield db_session

    app.dependency_overrides[get_relational_session] = _get
    yield db_session
    app.dependency_overrides = {}


@pytest.fixture
async def override_get_key_value_repository(get_redis_client):
    async def _get():
        yield get_redis_client

    app.dependency_overrides[get_key_value_repository] = _get
    yield get_redis_client
    app.dependency_overrides = {}


@pytest.fixture(scope="session")
def redis_container():
    with RedisContainer("redis:7.2.4") as redis:
        yield redis



@pytest.fixture
async def get_redis_client(redis_container):
    redis_pool = ConnectionPool(
        host=redis_container.get_container_host_ip(),
        port=redis_container.get_exposed_port(6379),
        decode_responses=True,
    )
    redis_client = Redis(connection_pool=redis_pool)
    try:
        yield redis_client
    finally:
        await redis_client.aclose()

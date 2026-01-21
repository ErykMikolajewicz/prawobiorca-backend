"""Common pytest fixtures for integration tests.

These fixtures handle container initialization (PostgreSQL, Redis)
and dependency overrides for FastAPI, ensuring test isolation.
"""

# The justification for the applied solutions is in the mkdocs documentation.
from typing import AsyncGenerator, Generator

import pytest
from redis import ConnectionPool as SyncRedisPool
from redis import Redis as SyncRedis
from redis.asyncio import ConnectionPool, Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer

import alembic.command
import alembic.config
from app.framework.dependencies.key_value_repository import get_key_value_repository
from app.infrastructure.relational_db.connection import get_relational_session
from main import app

REDIS_IMAGE_VERSION = "redis:8.0"
POSTGRES_IMAGE_VERSION = "postgres:17.5"


@pytest.fixture(scope="session", autouse=True)
def run_migrations(postgres_container: PostgresContainer) -> None:
    """Run Alembic migrations on the test PostgreSQL database.

    This fixture automatically runs before tests to ensure
    the schema is up to date.

    Args:
        postgres_container (PostgresContainer): Running PostgreSQL test container.
    """
    alembic_cfg = alembic.config.Config("alembic.ini")
    db_url = postgres_container.get_connection_url()
    alembic_cfg.set_main_option("sqlalchemy.url", db_url)
    alembic.command.upgrade(alembic_cfg, "head")


@pytest.fixture(scope="session")
def postgres_container() -> Generator[PostgresContainer, None]:
    """Create and manage a PostgreSQL test container.

    Scope is set to `session` to avoid repeated startup overhead.

    Yields:
        PostgresContainer: Running PostgreSQL container.
    """
    with PostgresContainer(POSTGRES_IMAGE_VERSION, driver="psycopg") as postgres:
        yield postgres


@pytest.fixture
async def override_get_relational_session(postgres_container: PostgresContainer) -> AsyncGenerator[None, None]:
    """Override the FastAPI relational DB dependency with a test session.

    Replaces the default `get_relational_session` dependency with a session
    connected to the PostgreSQL test container.

    Args:
        postgres_container (PostgresContainer): Running PostgreSQL test container.

    Yields:
        None: This is a pytest fixture that sets the override in FastAPI.

    Note:
        This fixture is intended for FastAPI integration tests only.
    """
    url = postgres_container.get_connection_url().replace("psycopg", "asyncpg")
    db_engine = create_async_engine(url, future=True, echo=False)
    async_session_maker = async_sessionmaker(db_engine, expire_on_commit=False, class_=AsyncSession)
    session = async_session_maker()

    async def _override():
        yield session

    app.dependency_overrides[get_relational_session] = _override
    yield
    await db_engine.dispose()
    app.dependency_overrides = {}


@pytest.fixture
async def relational_session(postgres_container: PostgresContainer) -> AsyncGenerator[AsyncSession, None]:
    """Provide a direct session to the test PostgreSQL database.

    Useful for inserting or cleaning up data before/after tests.

    Args:
        postgres_container (PostgresContainer): Running PostgreSQL test container.

    Yields:
        AsyncSession: SQLAlchemy async session with AUTOCOMMIT isolation.
    """
    url = postgres_container.get_connection_url().replace("psycopg", "asyncpg")
    db_engine = create_async_engine(url, future=True, echo=False, isolation_level="AUTOCOMMIT")
    async_session_maker = async_sessionmaker(db_engine, expire_on_commit=False, class_=AsyncSession)
    session = async_session_maker()
    try:
        yield session
    finally:
        await session.close()
        await db_engine.dispose()


@pytest.fixture(scope="session")
def redis_container() -> Generator[RedisContainer, None]:
    """Create and manage a Redis test container.

    Scope is set to `session` to avoid repeated startup overhead.

    Yields:
        RedisContainer: Running Redis container.
    """
    with RedisContainer(REDIS_IMAGE_VERSION) as redis:
        yield redis


@pytest.fixture
async def override_get_key_value_repository(redis_container: RedisContainer) -> AsyncGenerator[None, None]:
    """Override the FastAPI key-value repository dependency with a test Redis client.

    Replaces the default `get_key_value_repository` dependency with a Redis client
    connected to the test Redis container.

    Args:
        redis_container (RedisContainer): Running Redis test container.

    Yields:
        None: This is a pytest fixture that sets the override in FastAPI.

    Note:
        This fixture is intended for FastAPI integration tests only.
    """
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
def redis_client(redis_container: RedisContainer) -> Generator[SyncRedis, None]:
    """Provide a synchronous Redis client for direct access.

    Requires manual cleanup of stored keys between tests.

    Args:
        redis_container (RedisContainer): Running Redis test container.

    Yields:
        SyncRedis: Synchronous Redis client instance.
    """
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

"""Common pytest fixtures for integration tests.

These fixtures handle container initialization (PostgresSQL, Redis)
and dependency overrides for FastAPI, ensuring test isolation.
"""

# The justification for the applied solutions is in the mkdocs documentation.
from typing import AsyncGenerator, Generator

import alembic.command
import alembic.config
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer

from app.framework.dependencies.relational import get_relational_session
from main import app

POSTGRES_IMAGE_VERSION = "postgres:18"


@pytest.fixture(scope="session", autouse=True)
def run_migrations(postgres_container: PostgresContainer) -> None:
    """Run Alembic migrations on the test PostgresSQL database.

    This fixture automatically runs before tests to ensure
    the schema is up to date.

    Args:
        postgres_container (PostgresContainer): Running PostgresSQL test container.
    """
    alembic_cfg = alembic.config.Config("alembic.ini")
    db_url = postgres_container.get_connection_url()
    alembic_cfg.set_main_option("sqlalchemy.url", db_url)
    alembic.command.upgrade(alembic_cfg, "head")


@pytest.fixture(scope="session")
def postgres_container() -> Generator[PostgresContainer, None]:
    """Create and manage a PostgresSQL test container.

    Scope is set to `session` to avoid repeated startup overhead.

    Yields:
        PostgresContainer: Running PostgresSQL container.
    """
    with PostgresContainer(POSTGRES_IMAGE_VERSION, driver="psycopg") as postgres:
        yield postgres


@pytest.fixture
async def override_get_relational_session(postgres_container: PostgresContainer) -> AsyncGenerator[None, None]:
    """Override the FastAPI relational DB dependency with a test session.

    Replaces the default `get_relational_session` dependency with a session
    connected to the PostgresSQL test container.

    Args:
        postgres_container (PostgresContainer): Running PostgresSQL test container.

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
    """Provide a direct session to the test PostgresSQL database.

    Useful for inserting or cleaning up data before/after tests.

    Args:
        postgres_container (PostgresContainer): Running PostgresSQL test container.

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

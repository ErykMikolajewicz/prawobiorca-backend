import alembic.command
import alembic.config
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from testcontainers.postgres import PostgresContainer

from app.infrastructure.relational_db.connection import get_relational_session
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

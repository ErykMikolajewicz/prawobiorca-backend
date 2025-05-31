from contextlib import asynccontextmanager

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text

from app.config import settings


db_settings = settings.relational_db
DATABASE_URL = (f"{db_settings.DRIVER}://{db_settings.DB_USER}:{db_settings.PASSWORD}@"
                f"{db_settings.HOST}:{db_settings.PORT}/{db_settings.DB_NAME}")

engine = create_async_engine(
    DATABASE_URL,
    echo = False,
    pool_size = db_settings.POOL_SIZE,
    max_overflow = db_settings.MAX_OVERFLOW,
    pool_timeout = db_settings.POOL_TIMEOUT,
    pool_recycle = db_settings.POOL_RECYCLE
)

async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_relational_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session  # bad type hint from PyCharm


async def check_relational_db_connection():
    async with async_session_maker() as session:
        await session.execute(text('SELECT 1'))


class Base(DeclarativeBase):
    pass

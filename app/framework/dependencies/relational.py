from app.application.interfaces.relational import AsyncSession
from app.infrastructure.relational_db.connection import async_session_maker


async def get_relational_session() -> AsyncSession:
    session = async_session_maker()
    yield session
    await session.close()

from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.relational_db.connection import get_async_session

class BaseUnitOfWork:
    def __init__(self, session: Annotated[AsyncSession, Depends(get_async_session)]):
        self.session = session

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
        else:
            await self.commit()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
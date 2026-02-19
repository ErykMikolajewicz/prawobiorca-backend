from sqlalchemy.ext.asyncio import AsyncSession


class BaseUnitOfWork:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def __aenter__(self):
        await self.session.begin()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
        else:
            await self.__commit()

    async def __commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()

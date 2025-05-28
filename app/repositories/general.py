from typing import TypeVar, Type, Optional, Any, Generic
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete

from app.schemas.mixins import UuidIdMixin, IntIdMixin


ModelWithId = TypeVar('ModelWithId', bound=UuidIdMixin | IntIdMixin)


class CrudRepository(Generic[ModelWithId]):
    def __init__(self, db_session: AsyncSession, model: Type[ModelWithId]):
        self.db_session = db_session
        self.model: Type[ModelWithId] = model

    async def get(self, id_: UUID | int) -> Optional[ModelWithId]:
        select_statement = select(self.model).where(self.model.id == id_)
        return await self.db_session.scalar(select_statement)

    async def add(self, data: dict[str, Any]) -> ModelWithId:
        insert_stmt = insert(self.model).values(data).returning(self.model)
        result = await self.db_session.scalar(insert_stmt)
        await self.db_session.flush()
        await self.db_session.commit()
        return result

    async def update(self, id_: UUID | int, data: dict[str, Any]) -> Optional[ModelWithId]:
        update_statement = update(self.model).where(self.model.id == id_).values(data).returning(self.model)
        result = await self.db_session.scalar(update_statement)
        await self.db_session.flush()
        await self.db_session.commit()
        return result

    async def delete(self, id_: UUID | int):
        delete_statement = delete(self.model).where(self.model.id == id_)
        await self.db_session.execute(delete_statement)
        await self.db_session.flush()
        await self.db_session.commit()

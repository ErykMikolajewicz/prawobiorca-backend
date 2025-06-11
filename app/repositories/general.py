from typing import Any, Generic, Optional, Type, TypeVar
from uuid import UUID

from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.mixins import IntIdMixin, UuidIdMixin

ModelWithId = TypeVar("ModelWithId", bound=UuidIdMixin | IntIdMixin)


class CrudRepository(Generic[ModelWithId]):
    def __init__(self, session: AsyncSession, model: Type[ModelWithId]):
        self.session = session
        self.model: Type[ModelWithId] = model

    async def get(self, id_: UUID | int) -> Optional[ModelWithId]:
        select_statement = select(self.model).where(self.model.id == id_)
        return await self.session.scalar(select_statement)

    async def add(self, data: dict[str, Any]) -> ModelWithId:
        insert_stmt = insert(self.model).values(data).returning(self.model)
        result = await self.session.scalar(insert_stmt)
        await self.session.flush()
        return result

    async def update(self, id_: UUID | int, data: dict[str, Any]) -> Optional[ModelWithId]:
        update_statement = update(self.model).where(self.model.id == id_).values(data).returning(self.model)
        result = await self.session.scalar(update_statement)
        await self.session.flush()
        return result

    async def delete(self, id_: UUID | int):
        delete_statement = delete(self.model).where(self.model.id == id_)
        await self.session.execute(delete_statement)
        await self.session.flush()

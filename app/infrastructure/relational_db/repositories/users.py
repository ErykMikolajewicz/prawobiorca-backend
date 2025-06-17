from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import app.infrastructure.relational_db.schemas.users as user_schema
from app.infrastructure.relational_db.bases import CrudRepository


class UsersRepository(CrudRepository[user_schema.Users]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, user_schema.Users)

    async def get_by_email(self, email: str) -> Optional[user_schema.Users]:
        select_statement = select(self.model).where(self.model.email == email)
        result = await self.session.scalar(select_statement)
        return result


class UsersFilesRepository(CrudRepository[user_schema.UsersFiles]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, user_schema.UsersFiles)

from typing import Any, Annotated, Optional
import datetime

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

import app.schemas.users as user_schema
from app.repositories.general import CrudRepository
from app.relational_db.connection import get_async_session


class UsersRepository(CrudRepository[user_schema.Users]):
    def __init__(self, db_session: Annotated[AsyncSession, Depends(get_async_session)]):
        super().__init__(db_session, user_schema.Users)

    async def get_by_login(self, login: str) -> Optional[user_schema.Users]:
        select_statement = select(self.model).where(self.model.login == login)
        result = await self.db_session.scalar(select_statement)
        return result


class UsersTokensRepository:
    def __init__(self, db_session: Annotated[AsyncSession, Depends(get_async_session)]):
        self.db_session = db_session

    async def add(self, new_token: dict[str, Any]):
        insert_query = insert(user_schema.UsersAccessTokens).values(new_token)
        await self.db_session.execute(insert_query)
        await self.db_session.flush()
        await self.db_session.commit()

    async def check(self, access_token: str) -> user_schema.UsersAccessTokens:
        select_query = (select(user_schema.UsersAccessTokens).
                        where(user_schema.UsersAccessTokens.access_token == access_token,
                              user_schema.UsersAccessTokens.expiration_date > datetime.datetime.now()))
        token_data = await self.db_session.scalar(select_query)
        return token_data


class UserFilesRepository(CrudRepository[user_schema.UsersFiles]):
    def __init__(self, db_session: Annotated[AsyncSession, Depends(get_async_session)]):
        super().__init__(db_session, user_schema.UsersFiles)

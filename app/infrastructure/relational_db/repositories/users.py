from sqlalchemy import insert, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user import User
from app.domain.value_objects.user import CreateUserData
from app.infrastructure.relational_db.schemas.users import Users
from app.shared.exceptions import ObjectExists


class UsersRepository:
    def __init__(self, session: AsyncSession):
        self._session = session
        self._model = Users

    async def add(self, create_data: CreateUserData):
        insert_statement = insert(self._model).values(
            username=create_data.username, hashed_password=create_data.hashed_password
        )
        try:
            await self._session.execute(insert_statement)
        except IntegrityError:
            raise ObjectExists

    async def get_by_username(self, username: str) -> User | None:
        select_statement = select(self._model).where(self._model.username == username)
        result: Users = await self._session.scalar(select_statement)
        if result is None:
            return result

        user = User(result.id, result.username, result.hashed_password)
        return user

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import insert, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user import User
from app.domain.value_objects.user import CreateUserData
from app.infrastructure.relational_db.schemas.users import Users, UsersTokens
from app.shared.exceptions import ObjectExists


class UsersRepository:
    def __init__(self, session: AsyncSession):
        self._session = session
        self._model = Users

    async def add(self, create_data: CreateUserData):
        statement = insert(self._model).values(
            username=create_data.username, hashed_password=create_data.hashed_password
        )
        try:
            await self._session.execute(statement)
        except IntegrityError:
            raise ObjectExists

    async def get_by_username(self, username: str) -> User | None:
        statement = select(self._model).where(self._model.username == username)
        result: Users = await self._session.scalar(statement)
        if result is None:
            return result

        user = User(result.id, result.username, result.hashed_password)
        return user


class UsersTokensRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._model = UsersTokens

    async def get_user_id_by_session_id(self, session_id: str) -> str | None:
        statement = (
            select(self._model.user_id)
            .where(self._model.session_id == session_id and self._model.valid_until > datetime.now(timezone.utc))
            .limit(1)
        )

        result = await self._session.execute(statement)
        user = result.first()

        if user is None:
            return None

        user_id = str(user[0])
        return user_id

    async def add_session(self, user_id: UUID, session_id: str, valid_until: datetime) -> None:
        statement = insert(self._model).values(
            user_id=user_id,
            session_id=session_id,
            valid_until=valid_until,
        )
        await self._session.execute(statement)

    async def invalidate_session(self, session_id: str):
        statement = select(self._model).where(self._model.session_id == session_id)
        await self._session.execute(statement)

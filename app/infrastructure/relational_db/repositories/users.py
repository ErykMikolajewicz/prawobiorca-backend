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
    def __init__(self):
        self._model = Users

    async def add(self, session: AsyncSession, create_data: CreateUserData):
        statement = insert(self._model).values(
            username=create_data.username, hashed_password=create_data.hashed_password
        )
        try:
            await session.execute(statement)
        except IntegrityError:
            raise ObjectExists

    async def get_by_username(self, session: AsyncSession, username: str) -> User | None:
        statement = select(self._model).where(self._model.username == username)
        result: Users = await session.scalar(statement)
        if result is None:
            return result

        user = User(result.id, result.username, result.hashed_password)
        return user


class UsersTokensRepository:
    def __init__(self) -> None:
        self._model = UsersTokens

    async def get_user_id_by_session_id(self, session: AsyncSession, session_id: str) -> UUID | None:
        statement = (
            select(self._model.user_id)
            .where(self._model.session_id == session_id and self._model.valid_until > datetime.now(timezone.utc))
            .limit(1)
        )

        user_id = await session.scalar(statement)

        if user_id is None:
            return None

        user_id = UUID(str(user_id))

        return user_id

    async def add_session(self, session: AsyncSession, user_id: UUID, session_id: str, valid_until: datetime) -> None:
        statement = insert(self._model).values(
            user_id=user_id,
            session_id=session_id,
            valid_until=valid_until,
        )
        await session.execute(statement)

    async def invalidate_session(self, session: AsyncSession, session_id: str):
        statement = select(self._model).where(self._model.session_id == session_id)
        await session.execute(statement)

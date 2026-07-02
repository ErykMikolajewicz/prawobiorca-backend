from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import delete, insert, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dtos.user import CreateUserData
from app.domain.entities.user import User
from app.domain.value_objects.users import UserPrivileges
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

    async def get_user_privileges(self, session: AsyncSession, user_id: UUID) -> UserPrivileges | None:
        statement = select(self._model.is_admin).where(self._model.id == user_id)

        is_admin = await session.scalar(statement)
        if is_admin is None:
            return None

        is_admin = bool(is_admin)
        user_privileges = UserPrivileges(is_admin=is_admin)

        return user_privileges


class UsersTokensRepository:
    def __init__(self) -> None:
        self._model = UsersTokens

    async def get_user_id_by_authorization_token(self, session: AsyncSession, token: str) -> UUID | None:
        statement = (
            select(self._model.user_id)
            .where(self._model.session_id == token and self._model.valid_until > datetime.now(timezone.utc))
            .limit(1)
        )

        user_id = await session.scalar(statement)

        if user_id is None:
            return None

        user_id = UUID(str(user_id))

        return user_id

    async def add_token(self, session: AsyncSession, user_id: UUID, token: str, valid_until: datetime) -> None:
        statement = insert(self._model).values(
            user_id=user_id,
            session_id=token,
            valid_until=valid_until,
        )
        await session.execute(statement)

    async def invalidate_token(self, session: AsyncSession, token: str):
        statement = delete(self._model).where(self._model.session_id == token)
        await session.execute(statement)

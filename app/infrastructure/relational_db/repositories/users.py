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

    async def check_token_is_valid(self, token: str) -> bool:
        statement = select(self._model.valid_until).where(self._model.token == token).limit(1)

        result = await self._session.execute(statement)
        row = result.first()

        if row is None:
            return False

        valid_until: datetime = row[0]

        now_utc = datetime.now(timezone.utc)

        if valid_until.tzinfo is None:
            return valid_until >= now_utc.replace(tzinfo=None)

        return valid_until >= now_utc

    async def add_token(self, user_id: UUID, token: str, valid_until: datetime) -> None:
        statement = insert(self._model).values(
            user_id=user_id,
            token=token,
            valid_until=valid_until,
        )
        await self._session.execute(statement)

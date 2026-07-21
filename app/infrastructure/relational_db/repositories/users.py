from dataclasses import asdict
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import delete, insert, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dtos.user import CreateUserData
from app.domain.entities.user import User
from app.domain.value_objects.users import UserPrivileges
from app.infrastructure.relational_db.schemas.users import users_table, users_tokens_table
from app.shared.exceptions import ObjectExists


class UsersRepository:
    @staticmethod
    async def add(session: AsyncSession, create_data: CreateUserData):
        statement = insert(User).values(**asdict(create_data))
        try:
            await session.execute(statement)
        except IntegrityError:
            raise ObjectExists

    @staticmethod
    async def get_by_username(session: AsyncSession, username: str) -> User | None:
        statement = select(User).where(users_table.c.username == username)
        user = await session.scalar(statement)

        return user

    @staticmethod
    async def get_user_privileges(session: AsyncSession, user_id: UUID) -> UserPrivileges | None:
        statement = select(users_table.c.is_admin).where(users_table.c.id == user_id)

        result = await session.execute(statement)
        is_admin = result.scalar_one()
        if is_admin is None:
            return None

        user_privileges = UserPrivileges(is_admin=is_admin)

        return user_privileges


class UsersTokensRepository:
    @staticmethod
    async def get_user_id_by_authorization_token(session: AsyncSession, token: str) -> UUID | None:
        statement = (
            select(users_tokens_table.c.user_id)
            .where(
                users_tokens_table.c.session_id == token, users_tokens_table.c.valid_until > datetime.now(timezone.utc)
            )
            .limit(1)
        )

        user_id = await session.scalar(statement)

        return user_id

    @staticmethod
    async def add_token(session: AsyncSession, user_id: UUID, token: str, valid_until: datetime) -> None:
        statement = insert(users_tokens_table).values(
            user_id=user_id,
            session_id=token,
            valid_until=valid_until,
        )
        await session.execute(statement)

    @staticmethod
    async def invalidate_token(session: AsyncSession, token: str):
        statement = delete(users_tokens_table).where(users_tokens_table.c.session_id == token)
        await session.execute(statement)

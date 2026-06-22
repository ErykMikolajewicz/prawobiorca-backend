from datetime import datetime
from typing import Protocol
from uuid import UUID

from app.application.interfaces.relational import AsyncSession
from app.domain.entities.user import User
from app.domain.value_objects.user import CreateUserData


class UsersRepository(Protocol):
    async def add(self, session: AsyncSession, create_data: CreateUserData): ...

    async def get_by_username(self, session: AsyncSession, username: str) -> User | None: ...

    async def get_by_id(self, session: AsyncSession, id: UUID) -> User | None: ...


class UsersTokensRepository(Protocol):
    async def get_user_id_by_session_id(self, session: AsyncSession, session_id: str) -> UUID | None: ...

    async def add_session(
        self, session: AsyncSession, user_id: UUID, session_id: str, valid_until: datetime
    ) -> None: ...

    async def invalidate_session(self, session: AsyncSession, session_id: str): ...

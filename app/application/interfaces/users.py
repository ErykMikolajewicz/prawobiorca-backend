from datetime import datetime
from typing import Protocol
from uuid import UUID

from app.application.dtos.user import CreateUserData
from app.application.interfaces.relational import AsyncSession
from app.domain.entities.user import User
from app.domain.value_objects.users import UserPrivileges


class UsersRepository(Protocol):
    async def add(self, session: AsyncSession, create_data: CreateUserData): ...

    async def get_by_username(self, session: AsyncSession, username: str) -> User | None: ...

    async def get_user_privileges(self, session: AsyncSession, user_id: UUID) -> UserPrivileges | None: ...


class UsersTokensRepository(Protocol):
    async def get_user_id_by_authorization_token(self, session: AsyncSession, token: str) -> UUID | None: ...

    async def add_token(self, session: AsyncSession, user_id: UUID, token: str, valid_until: datetime) -> None: ...

    async def invalidate_token(self, session: AsyncSession, token: str): ...

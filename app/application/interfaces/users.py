from datetime import datetime
from typing import Protocol
from uuid import UUID

from app.domain.entities.user import User
from app.domain.value_objects.user import CreateUserData


class UsersRepository(Protocol):
    async def add(self, create_data: CreateUserData): ...

    async def get_by_username(self, username: str) -> User | None: ...


class UsersTokensRepository(Protocol):
    async def get_user_id_by_session_id(self, session_id: str) -> UUID | None: ...

    async def add_session(self, user_id: UUID, session_id: str, valid_until: datetime) -> None: ...

    async def invalidate_session(self, session_id: str): ...

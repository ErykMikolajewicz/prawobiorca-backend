from datetime import datetime
from typing import Protocol
from uuid import UUID

from app.domain.entities.user import User
from app.domain.value_objects.user import CreateUserData


class UsersRepository(Protocol):
    async def add_user(self, create_data: CreateUserData): ...

    async def get_by_username(self, username: str) -> User: ...


class UsersTokensRepository(Protocol):
    async def check_token_is_valid(self, token: str) -> bool: ...

    async def add_token(self, user_id: UUID, token: str, valid_until: datetime) -> None: ...

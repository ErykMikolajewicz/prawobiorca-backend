from typing import Protocol

from app.domain.entities.user import User
from app.domain.value_objects.user import CreateUserData


class UsersRepository(Protocol):
    async def add_user(self, create_data: CreateUserData): ...

    async def get_by_username(self, username: str) -> User: ...

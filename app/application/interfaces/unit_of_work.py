from typing import Protocol

from app.application.interfaces.users import UsersRepository


class AsyncUnitOfWork(Protocol):
    async def __aenter__(self): ...

    async def __aexit__(self, exc_type, exc_val, exc_tb): ...

    async def commit(self): ...

    async def rollback(self): ...


class UsersUnitOfWork(AsyncUnitOfWork):
    users: UsersRepository

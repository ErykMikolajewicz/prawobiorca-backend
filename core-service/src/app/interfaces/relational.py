from typing import Protocol, Self


class AsyncSession(Protocol):
    """Object of database session. Use to share session between repositories.
    Otherwise, use only when you want rollback session, without raising exception."""

    async def __aenter__(self) -> Self: ...

    async def __aexit__(self, exc_type, exc_val, exc_tb): ...

    async def rollback(self): ...

    """Rollback current transaction.
    After rollback you can only make selects. To make other queries start new transaction with SessionMaker."""


class SessionMaker(Protocol):
    def begin(self) -> AsyncSession: ...

    """Start transaction, user for insert, update, delete."""

    def __call__(self) -> AsyncSession: ...

    """Start connection, use when do not want to make transaction - practically for selects."""

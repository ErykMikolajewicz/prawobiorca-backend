from abc import ABC, abstractmethod
from typing import Any, Protocol, AsyncContextManager


class AbstractPipeline(Protocol, AsyncContextManager):
    async def delete(self, key: str) -> None:
        ...

    async def set(self, key: str, value: Any, ex: int | None = None) -> None:
        ...

    async def execute(self) -> None:
        ...


class KeyValueRepository(ABC):
    @abstractmethod
    async def set(self, key: str, value: Any, ex: int | None = None) -> None:
        ...

    @abstractmethod
    async def get(self, key: str) -> Any | None:
        ...

    @abstractmethod
    async def delete(self, key: str) -> None:
        ...

    @abstractmethod
    def pipeline(self) -> AsyncContextManager[AbstractPipeline]:
        ...

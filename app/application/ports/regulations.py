from collections.abc import Iterable
from typing import Protocol

from app.domain.value_objects.regulations import RegulationElement


class RegulationSplitter(Protocol):
    async def split(self, regulation: bytes) -> Iterable[RegulationElement]: ...

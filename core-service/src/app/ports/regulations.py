from collections.abc import Iterable
from typing import Protocol

from src.domain.value_objects.legal_units import RegulationElement


class RegulationSplitter(Protocol):
    async def split(self, regulation: bytes) -> Iterable[RegulationElement]: ...

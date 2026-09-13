from dataclasses import dataclass, field
from itertools import batched
from typing import Iterable
from uuid import UUID, uuid4

from src.domain.value_objects.legal_units import LegalUnitElement, UnitType
from src.shared.settings.application import app_settings


@dataclass
class SectionChunk:
    text: str
    embed_title: str | None = None
    chunk_index: int = 0
    vector: list[float] | None = None
    id: UUID = field(default_factory=uuid4)


@dataclass
class RegulationSection:
    header: str | None
    text: str
    chunks: list[SectionChunk]
    section_order: int | None = None
    unit_type: UnitType | None = None
    unit_number: str | None = None
    unit_path: list[str] | None = None
    elements: list[LegalUnitElement] = field(default_factory=list)
    id: UUID = field(default_factory=uuid4)


@dataclass
class SectionsCollection:
    _sections: list[RegulationSection]

    def __iter__(self) -> Iterable[RegulationSection]:
        return iter(self._sections)

    def get_chunks_batch_iterator(self) -> list[list[SectionChunk]]:
        chunks_to_embed = [chunk for section in self._sections for chunk in section.chunks]
        chunks_to_embed.sort(key=lambda chunk: len(chunk.text))

        batches = []
        for batch in batched(chunks_to_embed, app_settings.EMBED_DOCS_CHUNK_SIZE, strict=False):
            batches.append(batch)
        return batches

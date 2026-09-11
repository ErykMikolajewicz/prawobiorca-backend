from dataclasses import dataclass, field
from itertools import batched
from typing import Iterable
from uuid import UUID, uuid4

from src.domain.value_objects.legal_units import UnitType
from src.shared.settings.application import app_settings


@dataclass
class Document:
    title: str | None
    text: str
    chunk_order: int | None = None
    vector: list[float] | None = None
    unit_type: UnitType | None = None
    unit_number: str | None = None
    unit_path: list[str] | None = None
    part_index: int = 1
    parts_total: int = 1
    id: UUID = field(default_factory=uuid4)


@dataclass
class DocumentsCollection:
    _documents: list[Document]

    def __iter__(self) -> Iterable[Document]:
        return iter(self._documents)

    def get_batch_iterator(self) -> list[list[Document]]:
        chunks = []
        for chunk in batched(self._documents, app_settings.EMBED_DOCS_CHUNK_SIZE, strict=False):
            chunks.append(chunk)
        return chunks

    def __post_init__(self):
        self._documents.sort(key=lambda doc: len(doc.text))

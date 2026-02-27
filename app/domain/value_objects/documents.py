from dataclasses import dataclass, field
from typing import TypedDict
from uuid import UUID, uuid4


class DocumentPayload(TypedDict):
    text: str


@dataclass
class EmbeddedDocument:
    vector: list[float]
    payload: DocumentPayload
    id: UUID = field(default_factory=uuid4)

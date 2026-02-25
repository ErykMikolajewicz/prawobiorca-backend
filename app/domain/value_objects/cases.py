from dataclasses import dataclass
from uuid import UUID


@dataclass
class CaseData:
    case_id: UUID
    name: str

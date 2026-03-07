from dataclasses import dataclass
from uuid import UUID


@dataclass
class UserFile:
    file_hash: bytes
    user_id: UUID
    presentation_name: str

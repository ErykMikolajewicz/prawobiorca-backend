from dataclasses import dataclass
from uuid import UUID


@dataclass
class User:
    user_id: UUID
    username: str
    hashed_password: bytes

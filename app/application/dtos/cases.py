from uuid import UUID

from pydantic import BaseModel, Field


class NewCase(BaseModel):
    user_id: UUID
    name: str = Field(min_length=1)

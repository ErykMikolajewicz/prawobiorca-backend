from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.value_objects.regulations import RegulationType
from app.shared.consts import MAX_FILENAME_LENGTH, MIN_FILENAME_LENGTH


class RegulationData(BaseModel):
    name: str = Field(min_length=MIN_FILENAME_LENGTH, max_length=MAX_FILENAME_LENGTH)
    file: bytes = Field(min_length=1)
    document_type: RegulationType | None = None


class RegulationRepresentation(BaseModel):
    id: UUID
    presentation_name: str = Field(min_length=MIN_FILENAME_LENGTH,
                                   max_length=MAX_FILENAME_LENGTH,
                                   alias='presentationName')
    is_prepared: bool = Field(alias='isPrepared')

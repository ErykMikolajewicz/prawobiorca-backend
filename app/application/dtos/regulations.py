from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from pydantic.dataclasses import dataclass

from app.domain.value_objects.regulations import RegulationType
from app.shared.consts import MAX_FILENAME_LENGTH, MIN_FILENAME_LENGTH


class RegulationData(BaseModel):
    name: str = Field(min_length=MIN_FILENAME_LENGTH, max_length=MAX_FILENAME_LENGTH)
    file: bytes = Field(min_length=1)
    regulation_type: RegulationType | None = None


@dataclass(config=ConfigDict(alias_generator=to_camel))
class RegulationRepresentation:
    id: UUID
    is_prepared: bool
    presentation_name: str = Field(min_length=MIN_FILENAME_LENGTH, max_length=MAX_FILENAME_LENGTH)
    regulation_type: RegulationType | None = None

from pydantic import BaseModel, Field

from app.shared.consts import HASH_LENGTH, MAX_FILENAME_LENGTH, MIN_FILENAME_LENGTH


class FileData(BaseModel):
    name: str = Field(min_length=MIN_FILENAME_LENGTH, max_length=MAX_FILENAME_LENGTH)
    file: bytes = Field(min_length=1)


class FileRepresentation(BaseModel):
    file_hash: bytes = Field(min_length=HASH_LENGTH, max_length=HASH_LENGTH)
    presentation_name: str = Field(min_length=MIN_FILENAME_LENGTH, max_length=MAX_FILENAME_LENGTH)
    is_prepared: bool

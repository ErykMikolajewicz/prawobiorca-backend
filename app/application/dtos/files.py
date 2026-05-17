from pydantic import BaseModel, Field

from app.framework.dependencies.document_types import DocumentType
from app.shared.consts import HASH_LENGTH_BASE64, MAX_FILENAME_LENGTH, MIN_FILENAME_LENGTH


class FileData(BaseModel):
    name: str = Field(min_length=MIN_FILENAME_LENGTH, max_length=MAX_FILENAME_LENGTH)
    file: bytes = Field(min_length=1)
    document_type: DocumentType | None = None


class FileRepresentation(BaseModel):
    file_hash_str: str = Field(min_length=HASH_LENGTH_BASE64, max_length=HASH_LENGTH_BASE64)
    presentation_name: str = Field(min_length=MIN_FILENAME_LENGTH, max_length=MAX_FILENAME_LENGTH)
    is_prepared: bool

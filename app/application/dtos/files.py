from pydantic import BaseModel, Field, field_validator

from app.domain.exceptions import FileNameTooLong, InvalidCharacterInFileName


class FileData(BaseModel):
    file_name: str
    file: bytes = Field(min_length=1)

    @field_validator("file_name", mode="before")
    @classmethod
    def validate_file_name(cls, file_name: str) -> str:
        if "/" in file_name or "\x00" in file_name:
            raise InvalidCharacterInFileName(file_name)
        if len(file_name.encode("utf-8")) > 255:
            raise FileNameTooLong(file_name)
        return file_name

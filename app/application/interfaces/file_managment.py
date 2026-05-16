from typing import Protocol
from uuid import UUID

from app.application.dtos.files import FileRepresentation
from app.application.interfaces.relational import AsyncSession
from app.domain.value_objects.user_file import FileRegistrationData
from app.framework.dependencies.document_types import DocumentType


class PublicFileManager(Protocol):
    async def list_all_files(self, document_type: DocumentType | None = None) -> list[FileRepresentation]: ...


class UserFileManager(Protocol):
    def __init__(self, session: AsyncSession, user_id: UUID): ...

    async def list_user_files(self) -> list[FileRepresentation]: ...

    async def register_file(self, user_file: FileRegistrationData) -> None: ...

    async def unregister_file(self, file_hash: bytes) -> None: ...

    async def mark_as_prepared(self, file_hash: bytes) -> None: ...

    async def get_file_representation(self, file_hash: bytes) -> FileRepresentation: ...

from typing import Protocol
from uuid import UUID

from app.application.dtos.files import FileRepresentation
from app.domain.value_objects.user_file import UserFile


class PublicFileManager(Protocol):
    async def list_all_files(self) -> list[FileRepresentation]: ...


class UserFileManager(Protocol):
    async def list_user_files(self, user_id: UUID) -> list[FileRepresentation]: ...

    async def register_file(self, user_file: UserFile) -> None: ...

    async def unregister_file(self, user_id: UUID, file_hash: bytes) -> None: ...

    async def mark_as_prepared(self, user_id: UUID, file_hash: bytes) -> None: ...

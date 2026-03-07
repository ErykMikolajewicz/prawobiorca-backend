from uuid import UUID

from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dtos.files import FileRepresentation
from app.domain.value_objects.user_file import UserFile
from app.infrastructure.relational_db.schemas.files import PublicFiles, UsersFiles


class PublicFileManagerRepository:
    def __init__(self, session: AsyncSession):
        self._session = session
        self._model = PublicFiles

    async def list_all_files(self) -> list[FileRepresentation]:
        statement = select(self._model)
        result = await self._session.execute(statement)
        db_files = result.scalars().all()

        return [
            FileRepresentation(
                file_hash=file.file_hash, presentation_name=file.presentation_name, is_prepared=file.is_prepared
            )
            for file in db_files
        ]


class UserFileManagerRepository:
    def __init__(self, session: AsyncSession):
        self._session = session
        self._model = UsersFiles

    async def list_user_files(self, user_id: UUID) -> list[FileRepresentation]:
        statement = select(self._model).where(self._model.user_id == user_id)
        result = await self._session.execute(statement)
        db_files = result.scalars().all()

        return [
            FileRepresentation(
                file_hash=file.file_hash,
                presentation_name=file.presentation_name,
                is_prepared=file.is_prepared,
            )
            for file in db_files
        ]

    async def register_file(self, user_file: UserFile) -> None:
        statement = insert(self._model).values(
            user_id=user_file.user_id, file_hash=user_file.file_hash, presentation_name=user_file.presentation_name
        )

        try:
            await self._session.execute(statement)
        except IntegrityError:
            raise FileExistsError

    async def unregister_file(self, user_id: UUID, file_hash: bytes) -> None:
        statement = delete(self._model).where(self._model.user_id == user_id, self._model.file_hash == file_hash)
        result = await self._session.execute(statement)

        if result.rowcount == 0:
            raise FileNotFoundError

    async def mark_as_prepared(self, user_id: UUID, file_hash: bytes) -> None:
        statement = (
            update(self._model)
            .where(self._model.user_id == user_id, self._model.file_hash == file_hash)
            .values(is_prepared=True)
        )
        result = await self._session.execute(statement)

        if result.rowcount == 0:
            raise FileNotFoundError

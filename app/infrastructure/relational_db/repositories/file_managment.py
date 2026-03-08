import base64
from uuid import UUID

from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dtos.files import FileRepresentation
from app.domain.value_objects.user_file import FileRegistrationData
from app.infrastructure.relational_db.schemas.files import PublicFiles, UsersFiles


class PublicFileManagerRepository:
    def __init__(self, session: AsyncSession):
        self._session = session
        self._model = PublicFiles

    async def list_all_files(self) -> list[FileRepresentation]:
        statement = select(self._model)
        result = await self._session.execute(statement)
        db_files = result.scalars().all()

        files_representation = []
        for file in db_files:
            file_hash = base64.urlsafe_b64encode(file.hash)
            file_hash_str = file_hash.decode("utf-8")
            file_representation = FileRepresentation(
                file_hash_str=file_hash_str, presentation_name=file.presentation_name, is_prepared=file.is_prepared
            )
            files_representation.append(file_representation)
        return files_representation


class UserFileManagerRepository:
    def __init__(self, session: AsyncSession, user_id: UUID):
        self._session = session
        self._user_id = user_id
        self._model = UsersFiles

    async def list_user_files(self) -> list[FileRepresentation]:
        statement = select(self._model).where(self._model.user_id == self._user_id)
        result = await self._session.execute(statement)
        db_files = result.scalars().all()

        files_representation = []
        for file in db_files:
            file_hash = base64.urlsafe_b64encode(file.hash)
            file_hash_str = file_hash.decode("utf-8")
            file_representation = FileRepresentation(
                file_hash_str=file_hash_str, presentation_name=file.presentation_name, is_prepared=file.is_prepared
            )
            files_representation.append(file_representation)
        return files_representation

    async def register_file(self, user_file: FileRegistrationData) -> None:
        statement = insert(self._model).values(
            user_id=self._user_id, hash=user_file.hash, presentation_name=user_file.presentation_name
        )

        try:
            await self._session.execute(statement)
        except IntegrityError:
            raise FileExistsError

    async def unregister_file(self, file_hash: bytes) -> None:
        statement = delete(self._model).where(self._model.user_id == self._user_id, self._model.hash == file_hash)
        result = await self._session.execute(statement)

        if result.rowcount == 0:
            raise FileNotFoundError

    async def mark_as_prepared(self, file_hash: bytes) -> None:
        statement = (
            update(self._model)
            .where(self._model.user_id == self._user_id, self._model.hash == file_hash)
            .values(is_prepared=True)
        )
        result = await self._session.execute(statement)

        if result.rowcount == 0:
            raise FileNotFoundError

    async def get_file_representation(self, file_hash: bytes) -> FileRepresentation:
        statement = select(self._model.hash, self._model.presentation_name, self._model.is_prepared).where(
            self._model.user_id == self._user_id, self._model.hash == file_hash
        )
        result = await self._session.execute(statement)
        try:
            file_representation = result.one_or_none()
        except NoResultFound:
            raise FileNotFoundError

        file_hash = base64.urlsafe_b64encode(file_representation[0])
        file_hash_str = file_hash.decode("utf-8")

        return FileRepresentation(
            file_hash_str=file_hash_str,
            presentation_name=file_representation[1],
            is_prepared=file_representation[2],
        )

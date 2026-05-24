from uuid import UUID

from app.application.dtos.regulations import RegulationRepresentation
from app.infrastructure.relational_db.schemas.regulations import Regulations
from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.value_objects.regulations import RegulationType, RegulationRegistrationData


class RegulationsManagerRepository:
    def __init__(self, session: AsyncSession, user_id: UUID):
        self._session = session
        self._user_id = user_id
        self._model = Regulations

    async def list_user_files(self, regulation_type: RegulationType | None) -> list[RegulationRepresentation]:
        statement = select(self._model).where(self._model.user_id == self._user_id)

        if regulation_type is not None:
            statement = statement.where(self._model.document_type == regulation_type)

        result = await self._session.execute(statement)
        db_files = result.scalars().all()

        files_representation = []
        for file in db_files:
            file_representation = RegulationRepresentation(
                id=file.id,
                presentationName=file.presentation_name,
                isPrepared=file.is_prepared,
            )
            files_representation.append(file_representation)
        return files_representation

    async def register_file(self, user_file: RegulationRegistrationData) -> None:
        statement = insert(self._model).values(
            user_id=self._user_id,
            presentation_name=user_file.presentation_name,
            document_type=user_file.document_type,
        )

        try:
            await self._session.execute(statement)
        except IntegrityError:
            raise FileExistsError

    async def unregister_file(self, file_hash: bytes) -> None:
        statement = delete(self._model).where(self._model.user_id == self._user_id, self._model.id == file_hash)
        result = await self._session.execute(statement)

        if result.rowcount == 0:
            raise FileNotFoundError

    async def mark_as_prepared(self, file_hash: bytes) -> None:
        statement = (
            update(self._model)
            .where(self._model.user_id == self._user_id, self._model.id == file_hash)
            .values(is_prepared=True)
        )
        result = await self._session.execute(statement)

        if result.rowcount == 0:
            raise FileNotFoundError

    async def get_file_representation(self, file_hash: bytes) -> RegulationRepresentation:
        statement = select(self._model.id, self._model.presentation_name, self._model.is_prepared).where(
            self._model.user_id == self._user_id, self._model.id == file_hash
        )
        result = await self._session.execute(statement)
        try:
            file_representation = result.one_or_none()
        except NoResultFound:
            raise FileNotFoundError

        return RegulationRepresentation(
            id=file_representation[0],
            presentationName=file_representation[1],
            isPrepared=file_representation[2],
        )

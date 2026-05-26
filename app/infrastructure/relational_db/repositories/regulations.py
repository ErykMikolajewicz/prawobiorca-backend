from uuid import UUID

from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dtos.regulations import RegulationRepresentation
from app.domain.value_objects.regulations import RegulationRegistrationData, RegulationType
from app.infrastructure.relational_db.schemas.regulations import Regulations


class RegulationsManagerRepository:
    def __init__(self):
        self._model = Regulations

    async def list_regulations(
        self, session: AsyncSession, user_id: UUID | None, regulation_type: RegulationType | None
    ) -> list[RegulationRepresentation]:
        statement = select(self._model).where(self._model.user_id == user_id)

        if regulation_type is not None:
            statement = statement.where(self._model.regulation_type == regulation_type)

        result = await session.execute(statement)
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

    async def register_regulation(
        self, session: AsyncSession, user_id: UUID | None, regulation_registration_data: RegulationRegistrationData
    ) -> UUID:
        statement = (
            insert(self._model)
            .values(
                user_id=user_id,
                presentation_name=regulation_registration_data.presentation_name,
                document_type=regulation_registration_data.document_type,
            )
            .returning(self._model.id)
        )

        try:
            id_ = await session.scalar(statement)
        except IntegrityError:
            raise FileExistsError

        return id_

    async def unregister_regulation(self, session: AsyncSession, user_id: UUID | None, id_: UUID) -> None:
        statement = delete(self._model).where(self._model.user_id == user_id, self._model.id == id_)
        result = await session.execute(statement)

        if result.rowcount == 0:
            raise FileNotFoundError

    async def mark_as_prepared(self, session: AsyncSession, user_id: UUID | None, id_: UUID) -> None:
        statement = (
            update(self._model).where(self._model.user_id == user_id, self._model.id == id_).values(is_prepared=True)
        )
        result = await session.execute(statement)

        if result.rowcount == 0:
            raise FileNotFoundError

    async def get_regulation_representation(
        self, session: AsyncSession, user_id: UUID | None, id_: UUID
    ) -> RegulationRepresentation:
        statement = select(self._model.id, self._model.presentation_name, self._model.is_prepared).where(
            self._model.user_id == user_id, self._model.id == id_
        )
        result = await session.execute(statement)
        try:
            file_representation = result.one_or_none()
        except NoResultFound:
            raise FileNotFoundError

        return RegulationRepresentation(
            id=file_representation[0],
            presentationName=file_representation[1],
            isPrepared=file_representation[2],
        )

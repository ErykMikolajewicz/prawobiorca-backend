from uuid import UUID

from sqlalchemy import delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.interfaces.cases import CaseData
from app.infrastructure.relational_db.schemas.cases import Cases


class CasesRepository:
    def __init__(self, session: AsyncSession):
        self._session = session
        self._model = Cases

    async def list_by_user_id(self, user_id: UUID) -> list[CaseData]:
        statement = (
            select(self._model)
            .where(self._model.user_id == user_id)
            .order_by(self._model.create_date.desc())
        )
        result = await self._session.scalars(statement)

        return [
            CaseData(
                id=case.id,
                user_id=case.user_id,
                name=case.name,
                context=case.context,
                create_date=case.create_date,
            )
            for case in result.all()
        ]

    async def add(self, user_id: UUID, name: str, context: str | None = None) -> UUID:
        statement = (
            insert(self._model)
            .values(
                user_id=user_id,
                name=name,
                context=context,
            )
            .returning(self._model.id)
        )
        case_id = await self._session.scalar(statement)
        return case_id

    async def delete(self, case_id: UUID, user_id: UUID) -> None:
        statement = delete(self._model).where(self._model.id == case_id, self._model.user_id == user_id)
        await self._session.execute(statement)

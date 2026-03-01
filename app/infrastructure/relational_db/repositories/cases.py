from uuid import UUID

from sqlalchemy import delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dtos.cases import NewCase
from app.domain.value_objects.cases import CaseData
from app.infrastructure.relational_db.schemas.cases import Cases


class CasesRepository:
    def __init__(self, session: AsyncSession):
        self._session = session
        self._model = Cases

    async def list_by_user_id(self, user_id: UUID) -> list[CaseData]:
        statement = select(self._model).where(self._model.user_id == user_id).order_by(self._model.create_date.desc())
        result = await self._session.scalars(statement)

        cases = []
        for case in result.all():
            case_data = CaseData(case_id=str(case.id), name=case.name)
            cases.append(case_data)
        return cases

    async def add(self, new_case: NewCase) -> None:
        statement = insert(self._model).values(user_id=new_case.user_id, name=new_case.name).returning(self._model.id)
        await self._session.scalar(statement)

    async def delete(self, case_id: UUID) -> None:
        statement = delete(self._model).where(self._model.id == case_id)
        await self._session.execute(statement)

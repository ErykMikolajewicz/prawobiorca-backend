from dataclasses import dataclass
from uuid import UUID

from app.application.dtos.cases import NewCase
from app.application.interfaces.cases import CasesRepository
from app.application.interfaces.relational import AsyncSession
from app.domain.value_objects.cases import CaseData


@dataclass
class ListCases:
    session: AsyncSession
    cases_repo: CasesRepository
    user_id: UUID

    async def execute(self) -> list[CaseData]:
        async with self.session:
            cases = await self.cases_repo.list_by_user_id(self.user_id)
            return cases


@dataclass
class DeleteCase:
    session: AsyncSession
    cases_repo: CasesRepository
    case_id: UUID

    async def execute(self) -> None:
        async with self.session as session:
            await self.cases_repo.delete(self.case_id)
            await session.commit()


@dataclass
class AddCase:
    session: AsyncSession
    cases_repo: CasesRepository
    new_case: NewCase

    async def execute(self) -> None:
        async with self.session as session:
            await self.cases_repo.add(self.new_case)
            await session.commit()

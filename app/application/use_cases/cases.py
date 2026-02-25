from dataclasses import dataclass
from uuid import UUID

from app.application.interfaces.cases import CaseData, CasesRepository
from app.application.interfaces.relational import AsyncSession


@dataclass
class ListCases:
    session: AsyncSession
    cases_repo: CasesRepository
    user_id: UUID

    async def execute(self) -> list[CaseData]:
        async with self.session:
            return await self.cases_repo.list_by_user_id(self.user_id)


@dataclass
class DeleteCase:
    session: AsyncSession
    cases_repo: CasesRepository
    case_id: UUID
    user_id: UUID

    async def execute(self) -> None:
        async with self.session as session:
            await self.cases_repo.delete(self.case_id, self.user_id)
            await session.commit()


@dataclass
class AddCase:
    session: AsyncSession
    cases_repo: CasesRepository
    user_id: UUID
    name: str
    context: str | None = None

    async def execute(self) -> UUID:
        async with self.session as session:
            case_id = await self.cases_repo.add(
                user_id=self.user_id,
                name=self.name,
                context=self.context,
            )
            await session.commit()

        return case_id

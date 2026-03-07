from dataclasses import dataclass
from uuid import UUID

from app.application.dtos.cases import CaseArticleData, CaseData, NewCase, NewCaseArticle
from app.application.interfaces.cases import CaseArticlesRepository, CasesRepository
from app.application.interfaces.relational import AsyncSession


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


@dataclass
class AddCaseArticle:
    session: AsyncSession
    case_articles_repo: CaseArticlesRepository
    new_article: NewCaseArticle

    async def execute(self) -> None:
        async with self.session as session:
            await self.case_articles_repo.add(self.new_article)
            await session.commit()


@dataclass
class DeleteCaseArticle:
    session: AsyncSession
    case_articles_repo: CaseArticlesRepository
    article_id: UUID

    async def execute(self) -> None:
        async with self.session as session:
            await self.case_articles_repo.delete(self.article_id)
            await session.commit()


@dataclass
class ListCaseArticles:
    session: AsyncSession
    case_articles_repo: CaseArticlesRepository
    case_id: UUID

    async def execute(self) -> list[CaseArticleData]:
        async with self.session:
            case_articles = await self.case_articles_repo.list_by_case_id(self.case_id)
            return case_articles

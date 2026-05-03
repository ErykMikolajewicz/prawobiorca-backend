from uuid import UUID

from sqlalchemy import delete, insert, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dtos.cases import CaseArticleData, CaseData, NewCase, NewCaseArticle
from app.domain.exceptions import CaseNotFound
from app.infrastructure.relational_db.schemas.cases import CaseArticles, Cases


class CasesRepository:
    def __init__(self, session: AsyncSession):
        self._session = session
        self._model = Cases

    async def list_by_user_id(self, user_id: UUID) -> list[CaseData]:
        statement = select(self._model).where(self._model.user_id == user_id).order_by(self._model.create_date.desc())
        result = await self._session.scalars(statement)

        cases = []
        for case in result.all():
            case_data = CaseData(id=case.id, name=case.name)
            cases.append(case_data)
        return cases

    async def add(self, new_case: NewCase) -> UUID:
        statement = insert(self._model).values(user_id=new_case.user_id, name=new_case.name).returning(self._model.id)
        result = await self._session.scalar(statement)
        result = UUID(str(result))
        return result

    async def delete(self, case_id: UUID) -> None:
        statement = delete(self._model).where(self._model.id == case_id)
        await self._session.execute(statement)


class CaseArticlesRepository:
    def __init__(self, session: AsyncSession):
        self._session = session
        self._model = CaseArticles

    async def list_by_case_id(self, case_id: UUID) -> list[CaseArticleData]:
        statement = select(self._model).where(self._model.case_id == case_id)
        result = await self._session.scalars(statement)

        articles = []
        for article in result.all():
            article_data = CaseArticleData(
                id=article.id,
                caseId=article.case_id,
                presentationName=article.presentation_name,
                content=article.content,
            )
            articles.append(article_data)
        return articles

    async def add(self, case_id: UUID, new_article: NewCaseArticle) -> UUID:
        statement = (
            insert(self._model)
            .values(
                case_id=case_id,
                presentation_name=new_article.presentation_name,
                content=new_article.content,
            )
            .returning(self._model.id)
        )
        try:
            case_article_id = await self._session.scalar(statement)
        except IntegrityError:
            raise CaseNotFound
        case_article_id = UUID(str(case_article_id))
        return case_article_id

    async def delete(self, article_id: UUID) -> None:
        statement = delete(self._model).where(self._model.id == article_id)
        result = await self._session.execute(statement)

        if result.rowcount == 0:
            raise CaseNotFound

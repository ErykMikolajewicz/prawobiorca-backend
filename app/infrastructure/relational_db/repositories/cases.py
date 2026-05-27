from uuid import UUID

from sqlalchemy import delete, insert, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dtos.cases import CaseData, CaseDocument, NewCaseDocument
from app.domain.exceptions import CaseNotFound
from app.infrastructure.relational_db.schemas.cases import CaseDocuments, Cases


class CasesRepository:
    def __init__(self):
        self._model = Cases

    async def list_by_user_id(self, session: AsyncSession, user_id: UUID) -> list[CaseData]:
        statement = select(self._model).where(self._model.user_id == user_id).order_by(self._model.create_date.desc())
        result = await session.scalars(statement)

        cases = []
        for case in result.all():
            case_data = CaseData(id=case.id, name=case.name)
            cases.append(case_data)
        return cases

    async def add(self, session: AsyncSession, user_id: UUID, case_name: str) -> UUID:
        statement = insert(self._model).values(user_id=user_id, name=case_name).returning(self._model.id)
        result = await session.scalar(statement)
        result = UUID(str(result))
        return result

    async def delete(self, session: AsyncSession, user_id: UUID, case_id: UUID) -> None:
        statement = delete(self._model).where(self._model.id == case_id, self._model.user_id == user_id)
        await session.execute(statement)


class CaseDocumentsRepository:
    def __init__(self):
        self._model = CaseDocuments

    async def list_by_case_id(self, session: AsyncSession, user_id: UUID, case_id: UUID) -> list[CaseDocument]:
        statement = select(self._model).where(self._model.case_id == case_id, self._model.user_id == user_id)
        result = await session.scalars(statement)

        articles = []
        for article in result.all():
            article_data = CaseDocument(
                id=article.id,
                caseId=article.case_id,
                presentationName=article.presentation_name,
                content=article.content,
            )
            articles.append(article_data)
        return articles

    async def add(self, session: AsyncSession, user_id: UUID, case_id: UUID, new_document: NewCaseDocument) -> UUID:
        statement = (
            insert(self._model)
            .values(
                case_id=case_id,
                presentation_name=new_document.presentation_name,
                content=new_document.content,
                user_id=user_id,
            )
            .returning(self._model.id)
        )
        try:
            case_article_id = await session.scalar(statement)
        except IntegrityError:
            raise CaseNotFound
        case_article_id = UUID(str(case_article_id))
        return case_article_id

    async def delete(self, session: AsyncSession, user_id: UUID, article_id: UUID) -> None:
        statement = delete(self._model).where(self._model.id == article_id, self._model.user_id == user_id)
        result = await session.execute(statement)

        if result.rowcount == 0:
            raise CaseNotFound

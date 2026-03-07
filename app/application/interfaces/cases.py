from typing import Protocol
from uuid import UUID

from app.application.dtos.cases import CaseArticleData, CaseData, NewCase, NewCaseArticle


class CasesRepository(Protocol):
    async def list_by_user_id(self, user_id: UUID) -> list[CaseData]: ...

    async def add(self, new_case: NewCase) -> UUID: ...

    async def delete(self, case_id: UUID) -> None: ...


class CaseArticlesRepository(Protocol):
    async def list_by_case_id(self, case_id: UUID) -> list[CaseArticleData]: ...

    async def add(self, new_article: NewCaseArticle) -> UUID: ...

    async def delete(self, article_id: UUID) -> None: ...

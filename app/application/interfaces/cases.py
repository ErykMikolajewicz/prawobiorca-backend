from typing import Protocol
from uuid import UUID

from app.application.dtos.cases import NewCase, NewCaseArticle
from app.domain.value_objects.cases import CaseArticleData, CaseData


class CasesRepository(Protocol):
    async def list_by_user_id(self, user_id: UUID) -> list[CaseData]: ...

    async def add(self, new_case: NewCase) -> None: ...

    async def delete(self, case_id: UUID) -> None: ...


class CaseArticlesRepository(Protocol):
    async def list_by_case_id(self, case_id: UUID) -> list[CaseArticleData]: ...

    async def add(self, new_article: NewCaseArticle) -> None: ...

    async def delete(self, article_id: UUID) -> None: ...

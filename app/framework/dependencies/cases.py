from typing import Annotated
from uuid import UUID

from fastapi import Depends, Form, Path, Request

import app.infrastructure.relational_db.repositories.cases as sqla_repos
from app.application.dtos.cases import NewCase, NewCaseArticle
from app.application.interfaces.cases import CaseArticlesRepository, CasesRepository
from app.application.interfaces.relational import AsyncSession
from app.application.use_cases.cases import (
    AddCase,
    AddCaseArticle,
    DeleteCase,
    DeleteCaseArticle,
    ListCaseArticles,
    ListCases,
)
from app.framework.dependencies.relational import get_relational_session


def get_cases_repo(session: Annotated[AsyncSession, Depends(get_relational_session)]) -> CasesRepository:
    return sqla_repos.CasesRepository(session)


def get_case_articles_repo(session: Annotated[AsyncSession, Depends(get_relational_session)]) -> CaseArticlesRepository:
    return sqla_repos.CaseArticlesRepository(session)


def get_list_user_cases(
    session: Annotated[AsyncSession, Depends(get_relational_session)],
    cases_repository: Annotated[CasesRepository, Depends(get_cases_repo)],
    request: Request,
) -> ListCases:
    user_id = request.state.user_id
    return ListCases(session, cases_repository, user_id)


def get_add_user_case(
    session: Annotated[AsyncSession, Depends(get_relational_session)],
    cases_repository: Annotated[CasesRepository, Depends(get_cases_repo)],
    request: Request,
    case_name: Annotated[str, Form(...)],
) -> AddCase:
    user_id = request.state.user_id
    new_case = NewCase(user_id=user_id, name=case_name)
    return AddCase(session, cases_repository, new_case)


def get_delete_user_case(
    session: Annotated[AsyncSession, Depends(get_relational_session)],
    cases_repository: Annotated[CasesRepository, Depends(get_cases_repo)],
    case_id: Annotated[UUID, Path(alias="caseId")],
) -> DeleteCase:
    return DeleteCase(session, cases_repository, case_id)


def get_add_case_article(
    session: Annotated[AsyncSession, Depends(get_relational_session)],
    case_articles_repo: Annotated[CaseArticlesRepository, Depends(get_case_articles_repo)],
    case_id: Annotated[UUID, Form(...)],
    document_name: Annotated[str, Form(...)],
    article_content: Annotated[str, Form(...)],
) -> AddCaseArticle:
    new_article = NewCaseArticle(case_id=case_id, document_name=document_name, article_content=article_content)
    return AddCaseArticle(session, case_articles_repo, new_article)


def get_delete_case_article(
    session: Annotated[AsyncSession, Depends(get_relational_session)],
    case_articles_repo: Annotated[CaseArticlesRepository, Depends(get_case_articles_repo)],
    article_id: Annotated[UUID, Path(alias="articleId")],
) -> DeleteCaseArticle:
    return DeleteCaseArticle(session, case_articles_repo, article_id)


def get_list_case_articles(
    session: Annotated[AsyncSession, Depends(get_relational_session)],
    case_articles_repo: Annotated[CaseArticlesRepository, Depends(get_case_articles_repo)],
    case_id: UUID,
) -> ListCaseArticles:
    return ListCaseArticles(session, case_articles_repo, case_id)

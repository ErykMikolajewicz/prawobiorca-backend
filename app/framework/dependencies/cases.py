from typing import Annotated
from uuid import UUID

from fastapi import Depends, Form, Request

import app.infrastructure.relational_db.repositories.cases as sqla_repos
from app.application.dtos.cases import NewCase
from app.application.interfaces.cases import CasesRepository
from app.application.interfaces.relational import AsyncSession
from app.application.use_cases.cases import AddCase, DeleteCase, ListCases
from app.framework.dependencies.relational import get_relational_session


def get_cases_repo(session: Annotated[AsyncSession, Depends(get_relational_session)]) -> CasesRepository:
    return sqla_repos.CasesRepository(session)


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


def delete_user_case(
    session: Annotated[AsyncSession, Depends(get_relational_session)],
    cases_repository: Annotated[CasesRepository, Depends(get_cases_repo)],
    case_id: Annotated[UUID, Form(...)],
) -> DeleteCase:
    return DeleteCase(session, cases_repository, case_id)

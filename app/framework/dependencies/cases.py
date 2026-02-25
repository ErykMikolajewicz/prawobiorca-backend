from typing import Annotated

from fastapi import Depends, Request

import app.infrastructure.relational_db.repositories.cases as sqla_repos
from app.application.interfaces.cases import CasesRepository
from app.application.interfaces.relational import AsyncSession
from app.application.use_cases.cases import ListCases
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

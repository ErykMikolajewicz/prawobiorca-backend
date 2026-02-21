from typing import Annotated

from fastapi import Depends

import app.infrastructure.relational_db.repositories.users as sqla_repos
from app.application.interfaces.relational import AsyncSession
from app.application.interfaces.users import UsersRepository, UsersTokensRepository
from app.framework.dependencies.session import get_relational_session


async def get_users_tokens_repository(
    session: Annotated[AsyncSession, Depends(get_relational_session)],
) -> UsersTokensRepository:
    # TODO check why this type hint is bad
    return sqla_repos.UsersTokensRepository(session)


async def get_users_repository(session: Annotated[AsyncSession, Depends(get_relational_session)]) -> UsersRepository:
    return sqla_repos.UsersRepository(session)

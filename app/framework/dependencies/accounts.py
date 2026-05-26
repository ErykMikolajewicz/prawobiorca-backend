from typing import Annotated

from fastapi import Depends

from app.application.interfaces.relational import SessionMaker
from app.application.interfaces.users import UsersRepository
from app.application.use_cases.account import CreateAccount
from app.framework.dependencies.relational import get_session_maker
from app.framework.dependencies.users import get_users_repository


def get_create_account(
    session_maker: Annotated[SessionMaker, Depends(get_session_maker)],
    users_repo: Annotated[UsersRepository, Depends(get_users_repository)],
) -> CreateAccount:
    return CreateAccount(session_maker, users_repo)

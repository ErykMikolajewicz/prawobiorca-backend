import json
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status

from app.application.interfaces.relational import SessionMaker
from app.application.interfaces.users import UsersRepository, UsersTokensRepository
from app.application.use_cases.auth import LogoutUser
from app.domain.entities.user import User
from app.framework.dependencies.relational import get_session_maker
from app.framework.dependencies.users import get_users_repository, get_users_tokens_repository
from app.shared.consts import AUTHORIZATION_COOKIE_NAME


async def set_user_by_session_id(
    session_maker: Annotated[SessionMaker, Depends(get_session_maker)],
    users_tokens_repo: Annotated[UsersTokensRepository, Depends(get_users_tokens_repository)],
    request: Request,
):
    session_data = request.cookies.get(AUTHORIZATION_COOKIE_NAME)
    if session_data:
        session_data = json.loads(session_data)
        session_id = session_data["session_id"]
        async with session_maker() as session:
            user_id = await users_tokens_repo.get_user_id_by_session_id(session, session_id)
    else:
        user_id = None
        session_id = None

    request.state.user_id = user_id
    request.state.session_id = session_id


def get_logout_user(
    session_maker: Annotated[SessionMaker, Depends(get_session_maker)],
    tokens_repo: Annotated[UsersTokensRepository, Depends(get_users_tokens_repository)],
) -> LogoutUser:
    return LogoutUser(session_maker, tokens_repo)


async def require_logged_user(request: Request, _: Annotated[None, Depends(set_user_by_session_id)]) -> UUID:
    user_id = request.state.user_id

    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Login required!")

    return user_id


async def get_current_user(
    users_repo: Annotated[UsersRepository, Depends(get_users_repository)],
    session_maker: Annotated[SessionMaker, Depends(get_session_maker)],
    user_id: Annotated[UUID, Depends(require_logged_user)],
) -> User:

    async with session_maker() as session:
        user = await users_repo.get_by_id(session, user_id)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="login required")

    return user


async def require_admin(user: Annotated[User, Depends(get_current_user)]) -> User:
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="admin permission required")

    return user

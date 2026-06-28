import json
import logging
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status

from app.application.interfaces.relational import SessionMaker
from app.application.interfaces.users import UsersRepository, UsersTokensRepository
from app.application.use_cases.auth import LogoutUser
from app.domain.value_objects.users import UserPrivileges
from app.framework.dependencies.relational import get_session_maker
from app.framework.dependencies.users import get_users_repository, get_users_tokens_repository
from app.shared.consts import AUTHORIZATION_COOKIE_NAME

logger = logging.getLogger(__name__)


async def set_user_by_session_id(
    session_maker: Annotated[SessionMaker, Depends(get_session_maker)],
    users_tokens_repo: Annotated[UsersTokensRepository, Depends(get_users_tokens_repository)],
    users_repo: Annotated[UsersRepository, Depends(get_users_repository)],
    request: Request,
):
    user_id = None
    session_id = None
    user_privileges = None

    session_data = request.cookies.get(AUTHORIZATION_COOKIE_NAME)
    if session_data:
        session_data = json.loads(session_data)
        session_id = session_data["session_id"]
        async with session_maker() as session:
            user_id = await users_tokens_repo.get_user_id_by_session_id(session, session_id)
            if user_id:
                user_privileges = await users_repo.get_user_privileges(session, user_id)
            else:
                logger.error(f"User {user_id} for token {session_id} not found!")

    request.state.user_id = user_id
    request.state.session_id = session_id
    request.state.user_privileges = user_privileges


def get_logout_user(
    session_maker: Annotated[SessionMaker, Depends(get_session_maker)],
    tokens_repo: Annotated[UsersTokensRepository, Depends(get_users_tokens_repository)],
) -> LogoutUser:
    return LogoutUser(session_maker, tokens_repo)


async def require_logged_user(request: Request, _: Annotated[None, Depends(set_user_by_session_id)]) -> UUID:
    user_id = request.state.user_id

    if user_id is None:
        logger.warning(f"Unlogged user attempt to use endpoint: {request.base_url}!")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Login required!")

    return user_id


async def require_admin(request: Request, admin_id: Annotated[UUID, Depends(require_logged_user)]) -> UUID:
    user_privileges: UserPrivileges | None = request.state.user_privileges

    if user_privileges is None:
        logger.error(f"Privileges for user {admin_id} not found!")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User privileges unknown!")
    if not user_privileges.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin permission required!")

    return admin_id

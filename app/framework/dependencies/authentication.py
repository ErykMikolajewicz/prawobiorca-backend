import logging
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer

from app.application.interfaces.relational import SessionMaker
from app.application.interfaces.users import UsersRepository, UsersTokensRepository
from app.application.use_cases.auth import LogoutUser
from app.domain.value_objects.users import UserPrivileges
from app.framework.dependencies.relational import get_session_maker
from app.framework.dependencies.users import get_users_repository, get_users_tokens_repository
from app.shared.consts import AUTHORIZATION_COOKIE_NAME

logger = logging.getLogger(__name__)

_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login?delivery=json", auto_error=False)


async def authorize_user(
    session_maker: Annotated[SessionMaker, Depends(get_session_maker)],
    users_tokens_repo: Annotated[UsersTokensRepository, Depends(get_users_tokens_repository)],
    users_repo: Annotated[UsersRepository, Depends(get_users_repository)],
    header_token: Annotated[str | None, Depends(_oauth2_scheme)],
    request: Request,
):
    if header_token is not None:
        authorization_token = header_token
    else:
        authorization_token = request.cookies.get(AUTHORIZATION_COOKIE_NAME)

    user_id = None
    user_privileges = None
    if authorization_token is not None:
        async with session_maker() as session:
            user_id = await users_tokens_repo.get_user_id_by_authorization_token(session, authorization_token)
            if user_id:
                user_privileges = await users_repo.get_user_privileges(session, user_id)
            else:
                logger.warning(f"User for token {authorization_token} not found!")

    request.state.authorization_token = authorization_token
    request.state.user_id = user_id
    request.state.user_privileges = user_privileges


def get_logout_user(
    session_maker: Annotated[SessionMaker, Depends(get_session_maker)],
    tokens_repo: Annotated[UsersTokensRepository, Depends(get_users_tokens_repository)],
) -> LogoutUser:
    return LogoutUser(session_maker, tokens_repo)


async def require_logged_user(request: Request, _: Annotated[None, Depends(authorize_user)]) -> UUID:
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

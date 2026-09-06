import logging
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status

from app.application.interfaces.relational import SessionMaker
from app.application.interfaces.users import UsersRepository, UsersSessionsRepository
from app.application.use_cases.auth import LogoutUser, LogUser, RefreshTokens
from app.domain.exceptions.users import InvalidAccessToken
from app.domain.services.security import decode_access_token
from app.domain.value_objects.users import UserPrivileges
from app.framework.dependencies.relational import get_session_maker
from app.framework.dependencies.users import get_users_repository, get_users_sessions_repository
from app.shared.consts import ACCESS_COOKIE_NAME
from app.shared.settings.application import app_settings

logger = logging.getLogger(__name__)

jwt_secret_key = app_settings.JWT_SECRET_KEY
jwt_algorithm = app_settings.JWT_ALGORITHM


async def authorize_user(request: Request):
    access_token = request.cookies.get(ACCESS_COOKIE_NAME)

    claims = None
    if access_token is not None:
        try:
            claims = decode_access_token(access_token, jwt_secret_key, jwt_algorithm)
        except InvalidAccessToken:
            logger.warning("Request with invalid or expired access token!")

    request.state.session_id = claims.session_id if claims else None
    request.state.user_id = claims.user_id if claims else None
    request.state.user_privileges = UserPrivileges(is_admin=claims.is_admin) if claims else None


def get_log_user(
    session_maker: Annotated[SessionMaker, Depends(get_session_maker)],
    users_repo: Annotated[UsersRepository, Depends(get_users_repository)],
    sessions_repo: Annotated[UsersSessionsRepository, Depends(get_users_sessions_repository)],
) -> LogUser:
    return LogUser(session_maker, users_repo, sessions_repo)


def get_logout_user(
    session_maker: Annotated[SessionMaker, Depends(get_session_maker)],
    sessions_repo: Annotated[UsersSessionsRepository, Depends(get_users_sessions_repository)],
) -> LogoutUser:
    return LogoutUser(session_maker, sessions_repo)


def get_refresh_tokens(
    session_maker: Annotated[SessionMaker, Depends(get_session_maker)],
    users_repo: Annotated[UsersRepository, Depends(get_users_repository)],
    sessions_repo: Annotated[UsersSessionsRepository, Depends(get_users_sessions_repository)],
) -> RefreshTokens:
    return RefreshTokens(session_maker, users_repo, sessions_repo)


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

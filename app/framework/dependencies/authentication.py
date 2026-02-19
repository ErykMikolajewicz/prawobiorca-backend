from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import SecretStr
from redis.asyncio.client import Redis

from app.application.dtos.account import LoginData
from app.application.use_cases.auth import LogoutUser, LogUser
from app.domain.services.tokens import AccessTokensReader
from app.framework.dependencies.key_value_db import get_key_value_repository
from app.framework.dependencies.units_of_work import get_users_unit_of_work
from app.infrastructure.relational_db.units_of_work.users import UsersUnitOfWork


def get_access_tokens_reader(
    key_value_repo: Annotated[Redis, Depends(get_key_value_repository)],
) -> AccessTokensReader:
    return AccessTokensReader(key_value_repo)


async def validate_token(
    access_tokens_reader: Annotated[AccessTokensReader, Depends(get_access_tokens_reader)],
    token: Annotated[str, Depends(OAuth2PasswordBearer(tokenUrl="/auth/login"))],
    request: Request,
):
    user_id = await access_tokens_reader.get_user_by_access_token(token)
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    request.state.user_id = user_id
    request.state.access_token = token


def log_user_provider() -> type[LogUser]:
    return LogUser


def get_log_user(
    authentication_data: Annotated[OAuth2PasswordRequestForm, Depends(OAuth2PasswordRequestForm)],
    users_unit_of_work: Annotated[UsersUnitOfWork, Depends(get_users_unit_of_work)],
    log_user: Annotated[type[LogUser], Depends(log_user_provider)],
) -> LogUser:
    email = authentication_data.username
    password = authentication_data.password

    login_data = LoginData(username=email, password=SecretStr(password))
    return log_user(users_unit_of_work, login_data)


def get_logout_user(
    key_value_repo: Annotated[Redis, Depends(get_key_value_repository)],
    access_tokens_reader: Annotated[AccessTokensReader, Depends(get_access_tokens_reader)],
    request: Request,
) -> LogoutUser:
    user_id = request.state.user_id
    token = request.state.access_token
    return LogoutUser(key_value_repo, access_tokens_reader, token, user_id)

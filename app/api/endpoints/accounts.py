import asyncio
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import SecretStr
from redis.asyncio import Redis

import app.domain.services.accounts as account_services
from app.dependencies.authentication import validate_token
from app.shared.consts import SECURITY_MIN_RESPONSE_TIME
from app.shared.exceptions import InvalidCredentials, UserExists, UserNotFound
from app.infrastructure.utilities.security import url_safe_bearer_token_length
from app.domain.models.account import AccountCreate, LoginOutput
from app.infrastructure.relational_db.units_of_work.users import UsersUnitOfWork
from app.dependencies.units_of_work import get_users_unit_of_work
from app.dependencies.key_value_repository import get_key_value_repository


logger = logging.getLogger(__name__)

account_router = APIRouter(tags=["account"])


@account_router.post(
    "/accounts",
    status_code=status.HTTP_201_CREATED,
    responses={status.HTTP_409_CONFLICT: {"description": "User with that login already exist!"}},
)
async def create_account(account_data: AccountCreate, users_unit_of_work: UsersUnitOfWork = Depends(get_users_unit_of_work)):
    try:
        await account_services.create_account(users_unit_of_work, account_data)
    except UserExists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with that login already exist!")


@account_router.post(
    "/auth/login",
    responses={status.HTTP_401_UNAUTHORIZED: {"description": "Invalid credentials!" " Bad login or password."}},
)
async def log_user(
    authentication_data: Annotated[OAuth2PasswordRequestForm, Depends(OAuth2PasswordRequestForm)],
    key_value_repo: Annotated[Redis, Depends(get_key_value_repository)],
    users_unit_of_work: UsersUnitOfWork = Depends(get_users_unit_of_work),
) -> LoginOutput:
    execution_start_time = asyncio.get_event_loop().time()
    error_occurred = False

    login = authentication_data.username
    password = SecretStr(authentication_data.password)

    try:
        tokens = await account_services.log_user(login, password, key_value_repo, users_unit_of_work)
    except UserNotFound:
        logger.warning(f"Failed login attempt. User not found!")
        error_occurred = True
    except InvalidCredentials:
        logger.warning(f"Failed login attempt. Invalid password!")
        error_occurred = True

    # To prevent timeing attacks
    if error_occurred:
        elapsed_execution_time = asyncio.get_event_loop().time() - execution_start_time
        delay = max(0.0, SECURITY_MIN_RESPONSE_TIME - elapsed_execution_time)
        await asyncio.sleep(delay)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials!")

    return tokens


@account_router.post(
    "/auth/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={status.HTTP_401_UNAUTHORIZED: {"description": "Invalid access token!"}},
)
async def logout_user(
    key_value_repo: Annotated[Redis, Depends(get_key_value_repository)], login_data: Annotated[tuple[str, str], Depends(validate_token)]
):
    token, user_id = login_data
    await account_services.logout_user(token, user_id, key_value_repo)
    return None


@account_router.post(
    "/auth/refresh", responses={status.HTTP_401_UNAUTHORIZED: {"description": "Invalid refresh token!"}}
)
async def refresh(
    key_value_repo: Annotated[Redis, Depends(get_key_value_repository)],
    refresh_token: str = Header(
        ..., alias="X-Refresh-Token", min_length=url_safe_bearer_token_length, max_length=url_safe_bearer_token_length
    ),
) -> LoginOutput:
    try:
        tokens = await account_services.refresh(refresh_token, key_value_repo)
    except InvalidCredentials:
        logger.warning("Invalid refresh token!")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token!")
    return tokens

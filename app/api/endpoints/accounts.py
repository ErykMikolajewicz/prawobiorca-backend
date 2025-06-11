import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from redis.asyncio.client import Redis

import app.services.accounts as account_services
from app.core.authentication import validate_token
from app.core.exceptions import InvalidCredentials, UserExists, UserNotFound
from app.core.security import url_safe_bearer_token_length
from app.key_value_db.connection import get_redis
from app.models.account import AccountCreate, LoginOutput
from app.units_of_work.users import UsersUnitOfWork

logger = logging.getLogger(__name__)

account_router = APIRouter(tags=["account"])


@account_router.post(
    "/accounts",
    status_code=status.HTTP_201_CREATED,
    responses={status.HTTP_409_CONFLICT: {"description": "User with that login already exist!"}},
)
async def create_account(account_data: AccountCreate, users_unit_of_work: UsersUnitOfWork = Depends()):
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
    redis_client: Annotated[Redis, Depends(get_redis)],
    users_unit_of_work: UsersUnitOfWork = Depends(),
) -> LoginOutput:
    login = authentication_data.username
    password = authentication_data.password
    try:
        tokens = await account_services.log_user(login, password, redis_client, users_unit_of_work)
    except UserNotFound:
        logger.warning(f"Failed login attempt. User not found!")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials!")
    except InvalidCredentials:
        logger.warning(f"Failed login attempt, invalid password!")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials!")
    return tokens


@account_router.post(
    "/auth/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={status.HTTP_401_UNAUTHORIZED: {"description": "Invalid access token!"}},
)
async def logout_user(
    redis_client: Annotated[Redis, Depends(get_redis)], login_data: Annotated[tuple[str, str], Depends(validate_token)]
):
    token, user_id = login_data
    await account_services.logout_user(token, user_id, redis_client)
    return None


@account_router.post(
    "/auth/refresh", responses={status.HTTP_401_UNAUTHORIZED: {"description": "Invalid refresh token!"}}
)
async def refresh(
    redis_client: Annotated[Redis, Depends(get_redis)],
    refresh_token: str = Header(
        ..., alias="X-Refresh-Token", min_length=url_safe_bearer_token_length, max_length=url_safe_bearer_token_length
    ),
) -> LoginOutput:
    try:
        tokens = await account_services.refresh(refresh_token, redis_client)
    except InvalidCredentials:
        logger.warning("Invalid refresh token!")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token!")
    return tokens

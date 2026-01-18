import asyncio
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import SecretStr
from redis.asyncio import Redis
from starlette import status

from app.framework.models.auth import LoginOutput
from app.domain.services import accounts as account_services
from app.framework.api.endpoints.accounts import account_router, logger
from app.framework.dependencies.authentication import validate_token
from app.framework.dependencies.key_value_repository import get_key_value_repository
from app.framework.dependencies.units_of_work import get_users_unit_of_work
from app.infrastructure.relational_db.units_of_work.users import UsersUnitOfWork
from app.shared.consts import SECURITY_MIN_RESPONSE_TIME
from app.shared.exceptions import UserNotFound, InvalidCredentials, UserNotVerified
from app.framework.dependencies.authentication import get_refresh_tokens
from app.application.use_cases.auth import RefreshTokens



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

    email = authentication_data.username
    password = SecretStr(authentication_data.password)

    try:
        tokens = await account_services.log_user(email, password, key_value_repo, users_unit_of_work)
    except UserNotFound:
        logger.warning(f"Failed login attempt. User not found!")
    except InvalidCredentials:
        logger.warning(f"Failed login attempt. Invalid password!")
    except UserNotVerified:
        logger.warning(f"User with not verified email attempt to log!")
    else:
        return tokens

    # To prevent timeing attacks
    elapsed_execution_time = asyncio.get_event_loop().time() - execution_start_time
    delay = max(0.0, SECURITY_MIN_RESPONSE_TIME - elapsed_execution_time)
    await asyncio.sleep(delay)
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials!")


@account_router.post(
    "/auth/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={status.HTTP_401_UNAUTHORIZED: {"description": "Invalid access token!"}},
)
async def logout_user(
    key_value_repo: Annotated[Redis, Depends(get_key_value_repository)],
    login_data: Annotated[tuple[str, str], Depends(validate_token)],
):
    token, user_id = login_data
    await account_services.logout_user(token, user_id, key_value_repo)
    return None


@account_router.post(
    "/auth/refresh", responses={status.HTTP_401_UNAUTHORIZED: {"description": "Invalid refresh token!"}}
)
async def refresh(refresh_tokens: Annotated[RefreshTokens, Depends(get_refresh_tokens)]) -> LoginOutput:
    try:
        tokens = await refresh_tokens.execute()
    except InvalidCredentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token!")
    tokens = LoginOutput.model_validate(tokens)
    return tokens

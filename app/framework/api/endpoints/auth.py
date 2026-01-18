from typing import Annotated

from fastapi import Depends, HTTPException
from redis.asyncio import Redis
from starlette import status

from app.application.use_cases.auth import LogUser, RefreshTokens
from app.domain.services import accounts as account_services
from app.framework.api.endpoints.accounts import account_router
from app.framework.dependencies.authentication import get_log_user, get_refresh_tokens, validate_token
from app.framework.dependencies.key_value_repository import get_key_value_repository
from app.framework.models.auth import LoginOutput
from app.shared.exceptions import InvalidCredentials, UserCantLog


@account_router.post(
    "/auth/login",
    responses={status.HTTP_401_UNAUTHORIZED: {"description": "Invalid credentials! Bad login or password."}},
)
async def log_user(log_user_: Annotated[LogUser, Depends(get_log_user)]) -> LoginOutput:
    try:
        tokens = await log_user_.execute()
    except UserCantLog:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials!")

    return tokens


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

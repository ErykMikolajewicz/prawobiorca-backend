from typing import Annotated
from dataclasses import asdict

from fastapi import Depends, HTTPException, APIRouter
from starlette import status

from app.application.use_cases.auth import LogoutUser, LogUser, RefreshTokens
from app.framework.dependencies.authentication import get_log_user, get_logout_user, get_refresh_tokens, validate_token
from app.framework.models.auth import LoginOutput
from app.shared.exceptions import InvalidCredentials, UserCantLog

auth_router = APIRouter(tags=["account"])


@auth_router.post(
    "/auth/login",
    responses={status.HTTP_401_UNAUTHORIZED: {"description": "Invalid credentials! Bad login or password."}},
)
async def log_user(log_user_: Annotated[LogUser, Depends(get_log_user)]) -> LoginOutput:
    try:
        tokens = await log_user_.execute()
    except UserCantLog:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials!")

    return tokens


@auth_router.post(
    "/auth/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={status.HTTP_401_UNAUTHORIZED: {"description": "Invalid access token!"}},
    dependencies=[Depends(validate_token)],
)
async def logout_user(logout_user_: Annotated[LogoutUser, Depends(get_logout_user)]):
    await logout_user_.execute()


@auth_router.post(
    "/auth/refresh", responses={status.HTTP_401_UNAUTHORIZED: {"description": "Invalid refresh token!"}}
)
async def refresh(refresh_tokens: Annotated[RefreshTokens, Depends(get_refresh_tokens)]) -> LoginOutput:
    try:
        tokens = await refresh_tokens.execute()
    except InvalidCredentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token!")
    tokens = LoginOutput.model_validate(asdict(tokens))
    return tokens

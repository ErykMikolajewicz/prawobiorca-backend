from typing import Annotated

from fastapi import Depends, Header, HTTPException, Path, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from redis.asyncio.client import Redis

from app.application.dtos.account import LoginData
from app.application.use_cases.auth import LogUser, RefreshTokens
from app.domain.services.security import Secret, url_safe_bearer_token_length, url_safe_email_verification_token_length
from app.domain.services.tokens import EmailTokenVerifier
from app.framework.dependencies.key_value_repository import get_key_value_repository
from app.framework.dependencies.units_of_work import get_users_unit_of_work
from app.infrastructure.relational_db.units_of_work.users import UsersUnitOfWork
from app.shared.enums import KeyPrefix


async def validate_token(
    token: Annotated[str, Depends(OAuth2PasswordBearer(tokenUrl="/auth/login"))],
    request: Request,
    key_value_repo: Annotated[Redis, Depends(get_key_value_repository)],
) -> tuple[str, str]:
    user_id = await key_value_repo.get(f"{KeyPrefix.ACCESS_TOKEN}:{token}")
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    request.state.user_id = user_id
    request.state.access_token = token
    return token, user_id


def get_refresh_tokens(
    key_value_repo: Annotated[Redis, Depends(get_key_value_repository)],
    refresh_token: str = Header(
        alias="X-Refresh-Token", min_length=url_safe_bearer_token_length, max_length=url_safe_bearer_token_length
    ),
) -> RefreshTokens:
    return RefreshTokens(key_value_repo, refresh_token)


def get_email_token_verifier(
    key_value_repo: Annotated[Redis, Depends(get_key_value_repository)],
    verification_token: str = Path(
        min_length=url_safe_email_verification_token_length,
        max_length=url_safe_email_verification_token_length,
        alias="verificationToken",
    ),
):
    EmailTokenVerifier(key_value_repo, verification_token)


def get_log_user(
    authentication_data: Annotated[OAuth2PasswordRequestForm, Depends(OAuth2PasswordRequestForm)],
    key_value_repo: Annotated[Redis, Depends(get_key_value_repository)],
    users_unit_of_work: UsersUnitOfWork = Depends(get_users_unit_of_work),
) -> LogUser:
    email = authentication_data.username
    password = authentication_data.password
    password = Secret(password)

    login_data = LoginData(email, password)
    return LogUser(key_value_repo, users_unit_of_work, login_data)

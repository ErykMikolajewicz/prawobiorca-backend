from typing import Annotated

from fastapi import Depends, Header, HTTPException, Path, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from redis.asyncio.client import Redis

from app.application.dtos.account import LoginData
from app.application.use_cases.auth import LogoutUser, LogUser, RefreshTokens
from app.domain.services.security import Secret, url_safe_bearer_token_length, url_safe_email_verification_token_length
from app.domain.services.tokens import AccessTokensReader, EmailTokenVerifier
from app.framework.dependencies.key_value_repository import get_key_value_repository
from app.framework.dependencies.units_of_work import get_users_unit_of_work
from app.infrastructure.relational_db.units_of_work.users import UsersUnitOfWork


def get_access_tokens_reader(key_value_repo: Annotated[Redis, Depends(get_key_value_repository)]) -> AccessTokensReader:
    return AccessTokensReader(key_value_repo)


async def validate_token(
    access_tokens_reader: Annotated[AccessTokensReader, Depends(get_access_tokens_reader)],
    token: Annotated[str, Depends(OAuth2PasswordBearer(tokenUrl="/auth/login"))],
    request: Request,
):
    user_id = access_tokens_reader.get_user_by_access_token(token)
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    request.state.user_id = user_id
    request.state.access_token = token


def get_refresh_tokens(
    access_tokens_reader: Annotated[AccessTokensReader, Depends(get_access_tokens_reader)],
    key_value_repo: Annotated[Redis, Depends(get_key_value_repository)],
    refresh_token: str = Header(
        alias="X-Refresh-Token", min_length=url_safe_bearer_token_length, max_length=url_safe_bearer_token_length
    ),
) -> RefreshTokens:
    return RefreshTokens(key_value_repo, access_tokens_reader, refresh_token)


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
    access_tokens_reader: Annotated[AccessTokensReader, Depends(get_access_tokens_reader)],
    key_value_repo: Annotated[Redis, Depends(get_key_value_repository)],
    users_unit_of_work: UsersUnitOfWork = Depends(get_users_unit_of_work),
) -> LogUser:
    email = authentication_data.username
    password = authentication_data.password
    password = Secret(password)

    login_data = LoginData(email, password)
    return LogUser(key_value_repo, access_tokens_reader, users_unit_of_work, login_data)


def get_logout_user(
    key_value_repo: Annotated[Redis, Depends(get_key_value_repository)],
    access_tokens_reader: Annotated[AccessTokensReader, Depends(get_access_tokens_reader)],
    request: Request,
) -> LogoutUser:
    user_id = request.state.user_id
    token = request.state.access_token
    return LogoutUser(key_value_repo, access_tokens_reader, token, user_id)

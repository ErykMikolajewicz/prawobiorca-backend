from typing import Annotated
from uuid import UUID

from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, Request, HTTPException, status

from app.core.security import verify_password, generate_token, get_expiration_date
from app.config import settings
from app.core.exceptions import InvalidCredentials, UserNotFound
from app.models.token import AccessToken
from app.core.enums import TokenType
from app.units_of_work.users import UsersUnitOfWork


token_expiration_seconds = settings.app.USER_TOKEN_EXPIRATION_SECONDS


async def authenticate(login: str, password: str, users_unit_of_work: UsersUnitOfWork = Depends()) -> UUID:
    async with users_unit_of_work as uof:
        user = await uof.users.get_by_login(login)
    if user is None:
        raise UserNotFound('No user with that login!')
    hashed_password = user.hashed_password
    if not verify_password(password, hashed_password):
        raise InvalidCredentials('Invalid password!')
    return user.id


async def add_token(id_: UUID, users_unit_of_work: UsersUnitOfWork = Depends()) -> AccessToken:
    new_token = generate_token()
    expiration_date = get_expiration_date(token_expiration_seconds)
    token_data = {'id': id_, 'access_token': new_token, 'expiration_date': expiration_date}
    async with users_unit_of_work as uof:
        await uof.tokens.add(token_data)
    token = AccessToken(access_token = new_token, token_type=TokenType.bearer, expires_in=token_expiration_seconds)
    return token


async def validate_token(token: Annotated[str, Depends(OAuth2PasswordBearer(tokenUrl='/auth/login'))],
                         request: Request, users_unit_of_work: UsersUnitOfWork = Depends()):
    async with users_unit_of_work as uof:
        token_data = await uof.tokens.check(token)
    if token_data is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    request.state.token = token_data

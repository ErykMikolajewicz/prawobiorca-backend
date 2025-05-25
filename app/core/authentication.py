from typing import Annotated
from uuid import UUID

from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, Request, HTTPException, status

from app.repositories.users import Users, UsersTokens
from app.core.security import verify_password, generate_token, get_expiration_date
from app.config import settings


token_expiration_minutes = settings.app.USER_TOKEN_EXPIRATION_MINUTES


async def authenticate(login: str,
                       password: str,
                       users_repo: Annotated[Users, Depends(Users)]) -> UUID:
    user = await users_repo.get_by_login(login)
    if not verify_password(password, user.hashed_password):
        raise ValueError('Invalid password!')
    return user.id


async def add_token(id_: UUID,
                    users_tokens_repo: Annotated[UsersTokens, Depends(UsersTokens)]) -> str:
    new_token = generate_token()
    expiration_date = get_expiration_date(token_expiration_minutes)
    token_data = {'id': id_, 'access_token': new_token, 'expiration_date': expiration_date}
    await users_tokens_repo.add(token_data)
    return new_token


async def validate_token(token: Annotated[str, Depends(OAuth2PasswordBearer(tokenUrl='/employees/login'))],
                         request: Request,
                         users_tokens_repo: Annotated[UsersTokens, Depends(UsersTokens)]):
    token_data = await users_tokens_repo.check(token)
    if token_data is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    request.state.token = token_data

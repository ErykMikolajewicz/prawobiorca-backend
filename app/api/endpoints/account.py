import logging
from typing import Annotated

from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.models.account import AccountCreate
import app.services.accounts as account_services
from app.repositories.users import UsersRepository, UsersTokensRepository
from app.core.exceptions import UserExists, UserNotFound, InvalidCredentials
from app.core.authentication import authenticate, add_token
from app.models.token import AccessToken


logger = logging.getLogger(__name__)

account_router = APIRouter(
    tags=["account"]
)


@account_router.post("/accounts", status_code=status.HTTP_201_CREATED,
                     responses={status.HTTP_409_CONFLICT: {'description': 'User with that login already exist!'}})
async def create_account(
        account_data: AccountCreate,
        users_repo: UsersRepository = Depends()
        ):
    try:
        await account_services.create_account(users_repo, account_data)
    except UserExists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='User with that login already exist!')


@account_router.post('/auth/login',
                     responses={status.HTTP_401_UNAUTHORIZED: {'description': 'Invalid credentials!'
                                                                              ' Bad login or password.'}})
async def create_token(authentication_data: Annotated[OAuth2PasswordRequestForm, Depends(OAuth2PasswordRequestForm)],
                       users_repo: UsersRepository = Depends(),
                       users_tokens_repo: UsersTokensRepository = Depends()) -> AccessToken:
    login = authentication_data.username
    password = authentication_data.password
    try:
        id_ = await authenticate(login, password, users_repo)
    except UserNotFound:
        logger.warning(f'Failed login attempt. User not found!')
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials!')
    except InvalidCredentials:
        logger.warning(f'Failed login attempt, invalid password!')
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials!')
    token = await add_token(id_, users_tokens_repo)
    return token

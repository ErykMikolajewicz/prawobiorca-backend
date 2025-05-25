import logging
from typing import Annotated

from fastapi import APIRouter, Depends, status, HTTPException

from app.models.account import AccountCreate
import app.services.accounts as account_services
from app.repositories.users import UsersRepository
from app.core.exceptions import UserExistsException


logger = logging.getLogger(__name__)

account_router = APIRouter(
    tags=["account"]
)


@account_router.post("/account", status_code=status.HTTP_201_CREATED,
                     responses={status.HTTP_409_CONFLICT: {'description': 'User with that login already exist'}})
async def create_account(
        account_data: AccountCreate,
        users_repo: Annotated[UsersRepository, Depends(UsersRepository)]
        ):
    try:
        await account_services.create_account(users_repo, account_data)
    except UserExistsException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.message)

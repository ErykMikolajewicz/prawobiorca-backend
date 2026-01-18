import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.shared.exceptions import InvalidCredentials, UserExists
from app.framework.dependencies.accounts import get_create_account
from app.application.use_cases.account import CreateAccount
from app.framework.dependencies.accounts import get_verify_account
from app.application.use_cases.account import VerifyAccount

logger = logging.getLogger(__name__)

account_router = APIRouter(tags=["account"])


@account_router.post(
    "/accounts",
    status_code=status.HTTP_201_CREATED,
    responses={status.HTTP_409_CONFLICT: {"description": "User with that login already exist!"}},
)
async def create_account(create_account_: Annotated[CreateAccount, Depends(get_create_account)]):
    try:
        await create_account_.execute()
    except UserExists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with that email already exist!")


@account_router.post(
    "/accounts/verify/{verificationToken}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={status.HTTP_400_BAD_REQUEST: {"description": "Invalid or expired verification token!"}},
)
async def verify_account(verify_account_: Annotated[VerifyAccount ,Depends(get_verify_account)]):
    try:
        await verify_account_.execute()
    except InvalidCredentials:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification token!")

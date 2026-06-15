from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from app.application.dtos.account import LoginData
from app.application.use_cases.account import CreateAccount
from app.domain.exceptions import UserExists
from app.framework.dependencies.accounts import get_create_account

account_router = APIRouter(tags=["account"], prefix="/api")


@account_router.post(
    "/accounts/register",
    responses={
        status.HTTP_201_CREATED: {"description": "Account created."},
        status.HTTP_409_CONFLICT: {"description": "User with that login already exists."},
    },
)
async def create_account(login_data: LoginData, create_account_: Annotated[CreateAccount, Depends(get_create_account)]):

    try:
        await create_account_.execute(login_data)
    except UserExists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with that login already exists.")

    return JSONResponse({"ok": True}, status_code=status.HTTP_201_CREATED)

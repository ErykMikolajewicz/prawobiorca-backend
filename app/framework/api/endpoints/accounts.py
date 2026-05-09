from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from app.application.dtos.account import LoginData
from app.application.interfaces.relational import AsyncSession
from app.application.interfaces.users import UsersRepository
from app.application.use_cases.account import CreateAccount
from app.domain.exceptions import UserExists
from app.framework.dependencies.relational import get_relational_session
from app.framework.dependencies.users import get_users_repository

account_router = APIRouter(tags=["account"], prefix="/api")


@account_router.post(
    "/accounts/register", responses={status.HTTP_409_CONFLICT: {"description": "User with that login already exists."}}
)
async def create_account(
    login_data: LoginData,
    session: Annotated[AsyncSession, Depends(get_relational_session)],
    users_repo: Annotated[UsersRepository, Depends(get_users_repository)],
):

    create_account_ = CreateAccount(session, users_repo, login_data)

    try:
        await create_account_.execute()
    except UserExists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with that login already exists.")

    return JSONResponse({"ok": True})

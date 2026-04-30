import json
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse

from app.application.dtos.account import LoginData
from app.application.interfaces.relational import AsyncSession
from app.application.interfaces.users import UsersRepository, UsersTokensRepository
from app.application.use_cases.auth import LogoutUser, LogUser
from app.domain.exceptions import UserCantLog
from app.framework.dependencies.authentication import get_logout_user, set_user_by_session_id
from app.framework.dependencies.relational import get_relational_session
from app.framework.dependencies.users import get_users_repository, get_users_tokens_repository
from app.shared.consts import AUTHORIZATION_COOKIE_NAME

auth_router = APIRouter(tags=["auth"], prefix="/api/v2")


@auth_router.post("/auth/login")
async def log_user(
    session: Annotated[AsyncSession, Depends(get_relational_session)],
    users_repo: Annotated[UsersRepository, Depends(get_users_repository)],
    tokens_repo: Annotated[UsersTokensRepository, Depends(get_users_tokens_repository)],
    login_data: LoginData,
):

    log_user_ = LogUser(session, users_repo, tokens_repo, login_data)
    try:
        login_output = await log_user_.execute()
    except UserCantLog:
        error_message = "Nieprawidłowe dane logowania!"
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=error_message)

    login_output = login_output.model_dump()
    session_data = json.dumps(login_output)

    response = JSONResponse({"ok": True})
    response.set_cookie(
        key=AUTHORIZATION_COOKIE_NAME,
        value=session_data,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=60 * 60 * 24 * 7,
        path="/",
    )

    return response


@auth_router.get(
    "/auth/me",
    dependencies=[Depends(set_user_by_session_id)],
)
async def check_is_user_logged(request: Request):
    user_id = request.state.user_id

    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    else:
        return


@auth_router.post(
    "/auth/logout",
    dependencies=[Depends(set_user_by_session_id)],
)
async def logout_user(logout_user_: Annotated[LogoutUser, Depends(get_logout_user)]):
    await logout_user_.execute()

    response = JSONResponse({"ok": True})

    response.delete_cookie(
        key=AUTHORIZATION_COOKIE_NAME,
        path="/",
    )

    return response

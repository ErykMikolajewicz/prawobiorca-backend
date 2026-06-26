import json
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse

from app.application.dtos.account import LoginData
from app.application.interfaces.relational import SessionMaker
from app.application.interfaces.users import UsersRepository, UsersTokensRepository
from app.application.use_cases.auth import LogoutUser, LogUser
from app.domain.entities.user import User
from app.domain.exceptions import UserCantLog
from app.framework.dependencies.authentication import get_current_user, get_logout_user, set_user_by_session_id
from app.framework.dependencies.relational import get_session_maker
from app.framework.dependencies.users import get_users_repository, get_users_tokens_repository
from app.shared.consts import AUTHORIZATION_COOKIE_NAME

auth_router = APIRouter(tags=["auth"], prefix="/api")


@auth_router.post("/auth/login")
async def log_user(
    session_maker: Annotated[SessionMaker, Depends(get_session_maker)],
    users_repo: Annotated[UsersRepository, Depends(get_users_repository)],
    tokens_repo: Annotated[UsersTokensRepository, Depends(get_users_tokens_repository)],
    login_data: LoginData,
):

    log_user_ = LogUser(session_maker, users_repo, tokens_repo)
    try:
        login_output = await log_user_.execute(login_data)
    except UserCantLog:
        error_message = "incorrect logging data!"
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
)
async def check_is_user_logged(user: Annotated[User, Depends(get_current_user)]):
    return {"isLogged": True, "isAdmin": user.is_admin}


@auth_router.post(
    "/auth/logout",
    dependencies=[Depends(set_user_by_session_id)],
)
async def logout_user(logout_user_: Annotated[LogoutUser, Depends(get_logout_user)], request: Request):
    session_id = request.state.session_id
    await logout_user_.execute(session_id)

    response = JSONResponse({"ok": True})

    response.delete_cookie(
        key=AUTHORIZATION_COOKIE_NAME,
        path="/",
    )

    return response

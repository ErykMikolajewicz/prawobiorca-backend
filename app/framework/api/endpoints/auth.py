from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from app.application.dtos.account import LoginData
from app.application.interfaces.relational import SessionMaker
from app.application.interfaces.users import UsersRepository, UsersTokensRepository
from app.application.use_cases.auth import LogoutUser, LogUser
from app.domain.exceptions import UserCantLog
from app.domain.value_objects.users import UserPrivileges
from app.framework.dependencies.authentication import authorize_user, get_logout_user
from app.framework.dependencies.relational import get_session_maker
from app.framework.dependencies.users import get_users_repository, get_users_tokens_repository
from app.shared.consts import AUTHORIZATION_COOKIE_NAME

auth_router = APIRouter(tags=["auth"], prefix="/api")


@auth_router.post("/auth/login")
async def log_user(
    session_maker: Annotated[SessionMaker, Depends(get_session_maker)],
    users_repo: Annotated[UsersRepository, Depends(get_users_repository)],
    tokens_repo: Annotated[UsersTokensRepository, Depends(get_users_tokens_repository)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    delivery: Annotated[Literal["cookie", "json"], Query()] = "cookie",
):
    login_data = LoginData(username=form_data.username, password=form_data.password)

    log_user_ = LogUser(session_maker, users_repo, tokens_repo)
    try:
        login_output = await log_user_.execute(login_data)
    except UserCantLog:
        error_message = "incorrect logging data!"
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=error_message)

    token_string = login_output.session_id
    expiration_time = login_output.expires_in

    if delivery == "json":
        return {"access_token": token_string, "token_type": "bearer", "expires_in": expiration_time}

    response = JSONResponse({"ok": True})
    response.set_cookie(
        key=AUTHORIZATION_COOKIE_NAME,
        value=token_string,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=expiration_time,
        path="/api",
    )

    return response


@auth_router.get(
    "/auth/me",
    dependencies=[Depends(authorize_user)],
)
async def check_is_user_logged(request: Request):
    user_id = request.state.user_id
    user_privileges: UserPrivileges | None = request.state.user_privileges

    if user_id is None or user_privileges is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    else:
        return {"isAdmin": user_privileges.is_admin}


@auth_router.post(
    "/auth/logout",
    dependencies=[Depends(authorize_user)],
)
async def logout_user(logout_user_: Annotated[LogoutUser, Depends(get_logout_user)], request: Request):
    authorization_token = request.state.authorization_token
    await logout_user_.execute(authorization_token)

    response = JSONResponse({"ok": True})

    response.delete_cookie(
        key=AUTHORIZATION_COOKIE_NAME,
        path="/api",
    )

    return response

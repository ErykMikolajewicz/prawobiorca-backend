import json
from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import RedirectResponse
from pydantic import SecretStr

from app.application.dtos.account import LoginData
from app.application.interfaces.relational import AsyncSession
from app.application.interfaces.users import UsersRepository, UsersTokensRepository
from app.application.use_cases.auth import LogoutUser, LogUser
from app.domain.exceptions import UserCantLog
from app.framework.dependencies.authentication import get_logout_user, set_user_by_session_id
from app.framework.dependencies.relational import get_relational_session
from app.framework.dependencies.users import get_users_repository, get_users_tokens_repository
from app.framework.web.helpers import render_page_template
from app.shared.consts import AUTHORIZATION_COOKIE_NAME, FLASH_KEY

auth_router = APIRouter(tags=["auth"], prefix="/api")


@auth_router.get("/auth/login")
async def get_login_page(request: Request):
    return render_page_template(request, "login.html")


@auth_router.post("/auth/login")
async def log_user(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_relational_session)],
    users_repo: Annotated[UsersRepository, Depends(get_users_repository)],
    tokens_repo: Annotated[UsersTokensRepository, Depends(get_users_tokens_repository)],
    username: Annotated[str, Form(...)],
    password: Annotated[str, Form(...)],
):

    try:
        login_data = LoginData(username=username, password=SecretStr(password))
    except ValueError as e:
        error_message = str(e)
        request.session[FLASH_KEY] = {"error_message": error_message}
        return RedirectResponse(url="/api/auth/login", status_code=status.HTTP_303_SEE_OTHER)

    log_user_ = LogUser(session, users_repo, tokens_repo, login_data)
    try:
        login_output = await log_user_.execute()
    except UserCantLog:
        error_message = "Nieprawidłowe dane logowania!"
        request.session[FLASH_KEY] = {"error_message": error_message}
        return RedirectResponse(url="/api/auth/login", status_code=status.HTTP_303_SEE_OTHER)

    response = RedirectResponse(url="/api/", status_code=status.HTTP_303_SEE_OTHER)

    login_output = login_output.model_dump()
    session_data = json.dumps(login_output)
    response.set_cookie(
        key=AUTHORIZATION_COOKIE_NAME,
        value=session_data,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=60 * 60 * 24 * 7,
        path="/",
    )

    return response


@auth_router.post(
    "/auth/logout",
    dependencies=[Depends(set_user_by_session_id)],
)
async def logout_user(logout_user_: Annotated[LogoutUser, Depends(get_logout_user)]):
    await logout_user_.execute()

    response = RedirectResponse(url="/api/", status_code=status.HTTP_303_SEE_OTHER)

    response.delete_cookie(
        key=AUTHORIZATION_COOKIE_NAME,
        path="/",
    )

    return response

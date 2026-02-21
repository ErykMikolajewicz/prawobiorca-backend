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
from app.framework.dependencies.session import get_relational_session
from app.framework.dependencies.users import get_users_repository, get_users_tokens_repository
from app.framework.web.templating import templates
from app.shared.consts import AUTHORIZATION_COOKIE_NAME, FLASH_KEY

auth_router = APIRouter(tags=["auth"])


@auth_router.get("/auth/login")
async def get_login_page(request: Request):
    flash_data = request.session.pop(FLASH_KEY, None)
    if flash_data:
        try:
            error_message = flash_data["error_message"]
        except KeyError:
            error_message = ""
    else:
        error_message = ""

    return templates.TemplateResponse("login.html", {"request": request, "error_message": error_message})


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
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_303_SEE_OTHER)

    log_user_ = LogUser(session, users_repo, tokens_repo, login_data)
    try:
        session_id = await log_user_.execute()
    except UserCantLog:
        error_message = "Nieprawidłowe dane logowania!"
        request.session[FLASH_KEY] = {"error_message": error_message}
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_303_SEE_OTHER)

    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    response.set_cookie(
        key=AUTHORIZATION_COOKIE_NAME,
        value=session_id,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=60 * 60 * 24 * 7,
        path="/auth/login",
    )

    return response


@auth_router.post(
    "/auth/logout",
    dependencies=[Depends(set_user_by_session_id)],
)
async def logout_user(logout_user_: Annotated[LogoutUser, Depends(get_logout_user)]):
    await logout_user_.execute()

    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    response.delete_cookie(
        key=AUTHORIZATION_COOKIE_NAME,
        path="/auth/login",
    )

    return response

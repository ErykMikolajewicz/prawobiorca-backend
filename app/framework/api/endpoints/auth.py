from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import RedirectResponse
from pydantic import SecretStr

from app.application.dtos.account import LoginData
from app.application.interfaces.session import AsyncSession
from app.application.interfaces.users import UsersRepository, UsersTokensRepository
from app.application.use_cases.auth import LogoutUser, LogUser
from app.domain.exceptions import UserCantLog
from app.framework.dependencies.authentication import get_logout_user, log_user_provider, set_user_by_session_id
from app.framework.dependencies.session import get_relational_session
from app.framework.dependencies.users import get_users_repository, get_users_tokens_repository
from app.framework.web.templating import templates
from app.shared.consts import AUTHORIZATION_COOKIE_NAME

auth_router = APIRouter(tags=["auth"])


@auth_router.get("/auth/login")
async def get_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@auth_router.post("/auth/login")
async def log_user(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_relational_session)],
    log_user_class: Annotated[LogUser, Depends(log_user_provider)],
    users_repo: Annotated[UsersRepository, Depends(get_users_repository)],
    tokens_repo: Annotated[UsersTokensRepository, Depends(get_users_tokens_repository)],
    username: Annotated[str, Form(...)],
    password: Annotated[str, Form(...)],
):

    try:
        login_data = LoginData(username=username, password=SecretStr(password))
    except ValueError as e:
        password_verification_error = str(e)
        return templates.TemplateResponse(
            "register.html", {"request": request, "error_message": password_verification_error}
        )

    log_user_ = log_user_class(session, users_repo, tokens_repo, login_data)
    try:
        session_id = await log_user_.execute()
    except UserCantLog:
        return templates.TemplateResponse(
            "register.html", {"request": request, "error_message": "Nieprawidłowe dane logowania!"}
        )

    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    response.set_cookie(
        key=AUTHORIZATION_COOKIE_NAME,
        value=session_id,
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

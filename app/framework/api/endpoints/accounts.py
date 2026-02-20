from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import RedirectResponse
from pydantic import SecretStr

from app.application.dtos.account import LoginData
from app.application.interfaces.session import AsyncSession
from app.application.interfaces.users import UsersRepository
from app.application.use_cases.account import CreateAccount
from app.domain.exceptions import UserExists
from app.framework.dependencies.accounts import create_account_provider
from app.framework.dependencies.session import get_relational_session
from app.framework.dependencies.users import get_users_repository
from app.framework.web.templating import templates

account_router = APIRouter(tags=["account"])


@account_router.post("/accounts/register")
async def create_account(
    request: Request,
    username: Annotated[str, Form(...)],
    password: Annotated[str, Form(...)],
    session: Annotated[AsyncSession, Depends(get_relational_session)],
    users_repo: Annotated[UsersRepository, Depends(get_users_repository)],
    create_account_class: Annotated[type[CreateAccount], Depends(create_account_provider)],
):

    try:
        login_data = LoginData(username=username, password=SecretStr(password))
    except ValueError as e:
        password_verification_error = str(e)
        return templates.TemplateResponse(
            "register.html", {"request": request, "error_message": password_verification_error}
        )

    create_account_ = create_account_class(session, users_repo, login_data)

    try:
        await create_account_.execute()
    except UserExists:
        return templates.TemplateResponse(
            "register.html", {"request": request, "error_message": "Użytkownik z tą nazwą już istnieje!"}
        )

    return RedirectResponse(url="/auth/login", status_code=status.HTTP_303_SEE_OTHER)


@account_router.get("/accounts/register", status_code=status.HTTP_200_OK)
async def get_register_page(request: Request):
    return templates.TemplateResponse(
        "register.html",
        {"request": request, "error_message": "", "username": ""},
    )

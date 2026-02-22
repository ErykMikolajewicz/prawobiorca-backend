from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import RedirectResponse
from pydantic import SecretStr

from app.application.dtos.account import LoginData
from app.application.interfaces.relational import AsyncSession
from app.application.interfaces.users import UsersRepository
from app.application.use_cases.account import CreateAccount
from app.domain.exceptions import UserExists
from app.framework.dependencies.relational import get_relational_session
from app.framework.dependencies.users import get_users_repository
from app.framework.web.templating import templates
from app.shared.consts import FLASH_KEY

account_router = APIRouter(tags=["account"])


@account_router.post("/accounts/register")
async def create_account(
    request: Request,
    username: Annotated[str, Form(...)],
    password: Annotated[str, Form(...)],
    session: Annotated[AsyncSession, Depends(get_relational_session)],
    users_repo: Annotated[UsersRepository, Depends(get_users_repository)],
):
    try:
        login_data = LoginData(username=username, password=SecretStr(password))
    except ValueError as e:
        password_verification_error = str(e)
        request.session[FLASH_KEY] = {"error_message": password_verification_error}
        return RedirectResponse(url="/accounts/register", status_code=status.HTTP_303_SEE_OTHER)

    create_account_ = CreateAccount(session, users_repo, login_data)

    try:
        await create_account_.execute()
    except UserExists:
        request.session[FLASH_KEY] = {"error_message": f"Użytkownik o nazwie {username} już istnieje!"}
        return RedirectResponse(url="/accounts/register", status_code=status.HTTP_303_SEE_OTHER)

    return RedirectResponse(url="/auth/login", status_code=status.HTTP_303_SEE_OTHER)


@account_router.get("/accounts/register", status_code=status.HTTP_200_OK)
async def get_register_page(request: Request):
    flash_data = request.session.pop(FLASH_KEY, None)
    if flash_data:
        try:
            error_message = flash_data["error_message"]
        except KeyError:
            error_message = ""
    else:
        error_message = ""

    return templates.TemplateResponse(
        "register.html",
        {"request": request, "error_message": error_message},
    )

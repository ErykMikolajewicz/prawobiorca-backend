from typing import Annotated

from fastapi import Depends

from app.application.dtos.account import LoginData
from app.application.use_cases.account import CreateAccount, VerifyAccount
from app.domain.services.security import Secret
from app.domain.services.tokens import EmailTokenVerifier
from app.framework.dependencies.authentication import get_email_token_verifier
from app.framework.dependencies.units_of_work import get_users_unit_of_work
from app.framework.models.account import AccountCreate
from app.infrastructure.relational_db.units_of_work.users import UsersUnitOfWork


def create_account_provider() -> type[CreateAccount]:
    return CreateAccount


def get_create_account(
    account_data: AccountCreate,
    users_unit_of_work: UsersUnitOfWork = Depends(get_users_unit_of_work),
    create_account: type[CreateAccount] = Depends(create_account_provider)
) -> CreateAccount:
    email = account_data.email
    email = str(email)

    password = account_data.password
    password = password.get_secret_value()
    password = Secret(password)

    account_data = LoginData(email, password)
    return create_account(users_unit_of_work, account_data)


def verify_account_provider() -> type[VerifyAccount]:
    return VerifyAccount


def get_verify_account(
    email_token_verifier: Annotated[EmailTokenVerifier, Depends(get_email_token_verifier)],
    users_unit_of_work: Annotated[UsersUnitOfWork, Depends(get_users_unit_of_work)],
    verify_account: type[VerifyAccount] = Depends(verify_account_provider)
):
    return verify_account(email_token_verifier, users_unit_of_work)

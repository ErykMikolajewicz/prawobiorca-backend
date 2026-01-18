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


def get_create_account(
    account_data: AccountCreate, users_unit_of_work: UsersUnitOfWork = Depends(get_users_unit_of_work)
) -> CreateAccount:
    email = account_data.email
    email = str(email)

    password = account_data.password
    password = password.get_secret_value()
    password = Secret(password)

    account_data = LoginData(email, password)
    return CreateAccount(users_unit_of_work, account_data)


def get_verify_account(
    email_token_verifier: Annotated[EmailTokenVerifier, Depends(get_email_token_verifier)],
    users_unit_of_work: Annotated[UsersUnitOfWork, Depends(get_users_unit_of_work)],
):
    return VerifyAccount(email_token_verifier, users_unit_of_work)

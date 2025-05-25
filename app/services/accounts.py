from sqlalchemy.exc import IntegrityError

from app.models.account import AccountCreate
from app.repositories.users import UsersRepository
from app.core.security import hash_password
from app.core.exceptions import UserExistsException


async def create_account(user_repo: UsersRepository, account_data: AccountCreate):
    login = account_data.login
    password = account_data.password

    hashed_password = hash_password(password)
    account_hashed = {"login": login, "hashed_password": hashed_password}

    try:
        await user_repo.add(account_hashed)
    except IntegrityError:
        raise UserExistsException

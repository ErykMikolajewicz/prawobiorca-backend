from sqlalchemy.exc import IntegrityError

from app.models.account import AccountCreate
from app.core.security import hash_password
from app.core.exceptions import UserExists
from app.units_of_work.users import UsersUnitOfWork


async def create_account(users_unit_of_work: UsersUnitOfWork, account_data: AccountCreate):
    login = account_data.login
    password = account_data.password

    hashed_password = hash_password(password)
    account_hashed = {"login": login, "hashed_password": hashed_password}

    try:
        async with users_unit_of_work as uof:
            await uof.users.add(account_hashed)
    except IntegrityError:
        raise UserExists

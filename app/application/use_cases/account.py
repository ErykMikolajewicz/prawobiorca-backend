from dataclasses import dataclass
import logging

from app.application.dtos.account import AccountData
from app.infrastructure.relational_db.units_of_work.users import UsersUnitOfWork
from app.domain.services.security import hash_password
from app.domain.services.tokens import EmailTokenVerifier
from app.shared.exceptions import UserExists, RelationalDbIntegrityError
from app.shared.exceptions import InvalidCredentials

logger = logging.getLogger(__name__)


@dataclass
class CreateAccount:
    users_unit_of_work: UsersUnitOfWork
    account_data: AccountData

    async def execute(self):
        hashed_password = hash_password(self.account_data.password)
        account_hashed = {"email":self.account_data.email, "hashed_password": hashed_password}

        async with self.users_unit_of_work as uof:
            try:
                await uof.users.add(account_hashed)
            except RelationalDbIntegrityError:
                raise UserExists


@dataclass
class VerifyAccount:
    email_token_verifier: EmailTokenVerifier
    users_unit_of_work: UsersUnitOfWork

    async def execute(self):
        user_id = await self.email_token_verifier.get_user_id_by_token()
        if user_id is None:
            logger.warning("Invalid email verification token!")
            raise InvalidCredentials("Invalid email verification token!")

        async with self.users_unit_of_work as uow:
            await uow.users.verify_email(user_id)

        await self.email_token_verifier.invalidate_token()

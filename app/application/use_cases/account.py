import logging
from dataclasses import dataclass

from app.application.dtos.account import LoginData
from app.application.interfaces.unit_of_work import UsersUnitOfWork
from app.domain.exceptions import InvalidCredentials, UserExists
from app.domain.services.security import hash_password
from app.domain.services.tokens import EmailTokenVerifier
from app.domain.value_objects.user import CreateUserData
from app.shared.exceptions import ObjectExists

logger = logging.getLogger(__name__)


@dataclass
class CreateAccount:
    users_unit_of_work: UsersUnitOfWork
    login_data: LoginData

    async def execute(self):
        hashed_password = hash_password(self.login_data.password)
        create_user_data = CreateUserData(self.login_data.username, hashed_password)

        async with self.users_unit_of_work as uof:
            try:
                await uof.users.add(create_user_data)
            except ObjectExists:
                logger.warning("Can not add user, user with that username already exists!")
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

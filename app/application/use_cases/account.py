import logging
from dataclasses import dataclass

from app.application.dtos.account import LoginData
from app.application.interfaces.relational import AsyncSession
from app.application.interfaces.users import UsersRepository
from app.domain.exceptions import UserExists
from app.domain.services.security import hash_password
from app.domain.value_objects.user import CreateUserData
from app.shared.exceptions import ObjectExists

logger = logging.getLogger(__name__)


@dataclass
class CreateAccount:
    session: AsyncSession
    users_repo: UsersRepository
    login_data: LoginData

    async def execute(self):
        hashed_password = hash_password(self.login_data.password)
        create_user_data = CreateUserData(self.login_data.username, hashed_password)

        async with self.session as session:
            try:
                await self.users_repo.add(create_user_data)
            except ObjectExists:
                logger.warning("Can not add user, user with that username already exists!")
                raise UserExists
            await session.commit()

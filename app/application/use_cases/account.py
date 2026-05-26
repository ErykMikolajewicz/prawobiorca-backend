import logging
from dataclasses import dataclass

from app.application.dtos.account import LoginData
from app.application.interfaces.relational import SessionMaker
from app.application.interfaces.users import UsersRepository
from app.domain.exceptions import UserExists
from app.domain.services.security import hash_password
from app.domain.value_objects.user import CreateUserData
from app.shared.exceptions import ObjectExists

logger = logging.getLogger(__name__)


@dataclass
class CreateAccount:
    session_maker: SessionMaker
    users_repo: UsersRepository

    async def execute(self, login_data: LoginData):
        hashed_password = hash_password(login_data.password)
        create_user_data = CreateUserData(login_data.username, hashed_password)

        async with self.session_maker.begin() as session:
            try:
                await self.users_repo.add(session, create_user_data)
            except ObjectExists:
                logger.warning("Can not add user, user with that username already exists!")
                raise UserExists

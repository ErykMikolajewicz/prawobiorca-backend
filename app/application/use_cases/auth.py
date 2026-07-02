import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from app.application.dtos.account import LoginData
from app.application.dtos.auth import LoginOutput
from app.application.interfaces.relational import SessionMaker
from app.application.interfaces.users import UsersRepository, UsersTokensRepository
from app.application.services.accounts import check_user_can_log
from app.domain.exceptions import UserCantLog
from app.domain.services.security import generate_authorization_token, prevent_timing_attack
from app.framework.dependencies.file_storage import app_settings

logger = logging.getLogger(__name__)

session_id_expiration_seconds = app_settings.SESSION_ID_EXPIRATION_SECONDS


@dataclass
class LogUser:
    session_maker: SessionMaker
    users_repo: UsersRepository
    tokens_repo: UsersTokensRepository

    async def execute(self, login_data: LoginData):
        execution_start_time = asyncio.get_event_loop().time()

        async with self.session_maker() as session:
            user_id = await check_user_can_log(session, self.users_repo, login_data)
        if user_id is None:
            await prevent_timing_attack(execution_start_time)
            raise UserCantLog

        token = generate_authorization_token()
        valid_until = datetime.now(timezone.utc) + timedelta(seconds=session_id_expiration_seconds)

        async with self.session_maker.begin() as session:
            await self.tokens_repo.add_token(session, user_id, token, valid_until)

        return LoginOutput(session_id=token, expires_in=session_id_expiration_seconds)


@dataclass
class LogoutUser:
    session_maker: SessionMaker
    tokens_repo: UsersTokensRepository

    async def execute(self, authorization_token: str):

        async with self.session_maker.begin() as session:
            await self.tokens_repo.invalidate_token(session, authorization_token)

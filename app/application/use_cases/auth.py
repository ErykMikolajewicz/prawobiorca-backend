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
from app.domain.services.security import generate_session_id, prevent_timing_attack
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

        session_id = generate_session_id()
        valid_until = datetime.now(timezone.utc) + timedelta(seconds=session_id_expiration_seconds)

        async with self.session_maker.begin() as session:
            await self.tokens_repo.add_session(session, user_id, session_id, valid_until)

        return LoginOutput(session_id=session_id, expires_in=session_id_expiration_seconds)


@dataclass
class LogoutUser:
    session_maker: SessionMaker
    tokens_repo: UsersTokensRepository

    async def execute(self, session_id: str):

        async with self.session_maker.begin() as session:
            await self.tokens_repo.invalidate_session(session, session_id)

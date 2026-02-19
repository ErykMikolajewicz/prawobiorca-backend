import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from redis.asyncio import Redis

from app.application.dtos.account import LoginData
from app.application.interfaces.unit_of_work import UsersUnitOfWork
from app.domain.entities.tokens import AccessTokenData
from app.domain.exceptions import UserCantLog
from app.domain.services.accounts import check_user_can_log
from app.domain.services.security import generate_token, prevent_timing_attack
from app.domain.services.tokens import AccessTokensManager, AccessTokensReader
from app.shared.enums import TokenType

logger = logging.getLogger(__name__)
SESSION_DURATION_SECONDS = 30 * 60


@dataclass
class LogUser:
    users_unit_of_work: UsersUnitOfWork
    login_data: LoginData

    async def execute(self):
        execution_start_time = asyncio.get_event_loop().time()

        user_id = await check_user_can_log(self.users_unit_of_work, self.login_data)
        if user_id is None:
            await prevent_timing_attack(execution_start_time)
            raise UserCantLog

        access_token = generate_token()
        valid_until = datetime.now(timezone.utc) + timedelta(seconds=SESSION_DURATION_SECONDS)

        async with self.users_unit_of_work as uow:
            await uow.users_tokens.add_token(user_id, access_token, valid_until)

        return AccessTokenData(
            access_token=access_token,
            expires_in=SESSION_DURATION_SECONDS,
            token_type=TokenType.BEARER,
        )


@dataclass
class LogoutUser:
    key_value_repo: Redis
    access_tokens_reader: AccessTokensReader
    access_token: str
    user_id: str

    async def execute(self):
        refresh_token = await self.access_tokens_reader.get_refresh_token_by_user(self.user_id)

        if refresh_token is None:
            logger.error("Invalid application state, no refresh token for user!")

        async with self.key_value_repo.pipeline() as pipeline:
            access_token_manager = AccessTokensManager(pipeline)

            if refresh_token is not None:
                await access_token_manager.invalidate_refresh_token(refresh_token)

            await access_token_manager.invalidate_refresh_token_user(self.user_id)
            await access_token_manager.invalidate_access_token(self.access_token)
            await pipeline.execute()

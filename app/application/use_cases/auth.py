import asyncio
import logging
from dataclasses import dataclass

from redis.asyncio import Redis

from app.application.dtos.account import LoginData
from app.domain.entities.tokens import RefreshTokenData
from app.domain.services.accounts import check_user_can_log
from app.domain.services.security import prevent_timing_attack
from app.domain.services.tokens import AccessTokensManager, AccessTokensReader
from app.infrastructure.relational_db.units_of_work.users import UsersUnitOfWork
from app.shared.exceptions import InvalidCredentials, UserCantLog

logger = logging.getLogger(__name__)


@dataclass
class RefreshTokens:
    key_value_repo: Redis
    access_tokens_reader: AccessTokensReader
    refresh_token: str

    async def execute(self) -> RefreshTokenData:
        user_id = await self.access_tokens_reader.get_user_by_refresh_token(self.refresh_token)
        if user_id is None:
            logger.warning("Invalid refresh token!")
            raise InvalidCredentials("Invalid refresh token!")

        async with self.key_value_repo.pipeline() as pipeline:
            access_token_manager = AccessTokensManager(pipeline)

            await access_token_manager.invalidate_refresh_token(self.refresh_token)
            tokens = await access_token_manager.refresh_tokens(user_id)
            await pipeline.execute()
        return tokens


@dataclass
class LogUser:
    key_value_repo: Redis
    access_tokens_reader: AccessTokensReader
    users_unit_of_work: UsersUnitOfWork
    login_data: LoginData

    async def execute(self):
        execution_start_time = asyncio.get_event_loop().time()

        user_id = await check_user_can_log(self.users_unit_of_work, self.login_data)
        if user_id is None:
            await prevent_timing_attack(execution_start_time)
            raise UserCantLog

        previous_refresh_token = await self.access_tokens_reader.get_refresh_token_by_user(user_id)
        if previous_refresh_token is not None:
            logger.warning("User with existing refresh token logging.")

        async with self.key_value_repo.pipeline() as pipeline:
            access_token_manager = AccessTokensManager(pipeline)

            if previous_refresh_token is not None:
                await access_token_manager.invalidate_refresh_token(previous_refresh_token)

            tokens = await access_token_manager.refresh_tokens(user_id)
            await pipeline.execute()
        return tokens


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

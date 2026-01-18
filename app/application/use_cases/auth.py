from dataclasses import dataclass
import logging

from redis.asyncio import Redis
from app.domain.services.tokens import AccessTokenManager
from app.shared.exceptions import InvalidCredentials
from app.domain.entities.tokens import RefreshTokenData

logger = logging.getLogger(__name__)


@dataclass
class RefreshTokens:
    key_value_repo: Redis
    refresh_token: str

    async def execute(self) -> RefreshTokenData:
        async with self.key_value_repo.pipeline() as pipeline:
            access_token_manager = AccessTokenManager(pipeline)

            user_id = await access_token_manager.get_user_by_refresh_token(self.refresh_token)
            if user_id is None:
                logger.warning("Invalid refresh token!")
                raise InvalidCredentials("Invalid verification token!")

            tokens = await access_token_manager.refresh_tokens(self.refresh_token, user_id)
        return tokens

from typing import Optional

from redis.asyncio import Redis
from redis.asyncio.client import Pipeline

from app.domain.entities.tokens import RefreshTokenData
from app.domain.services.security import generate_token
from app.shared.settings.application import app_settings
from app.shared.enums import KeyPrefix, TokenType

access_token_expiration_seconds = app_settings.ACCESS_TOKEN_EXPIRATION_SECONDS
refresh_token_expiration_seconds = app_settings.REFRESH_TOKEN_EXPIRATION_SECONDS


class AccessTokenManager:
    def __init__(self, key_value_session: Pipeline):
        self._key_value_session = key_value_session

    async def get_user_by_refresh_token(self, refresh_token) -> Optional[str]:
        user_id = await self._key_value_session.get(f"{KeyPrefix.REFRESH_TOKEN}:{refresh_token}")
        return user_id

    async def get_refresh_token_by_user(self, user_id: str) -> str:
        refresh_token = await self._key_value_session.get(f"{KeyPrefix.USER_REFRESH_TOKEN}:{user_id}")
        return refresh_token

    async def invalidate_refresh_token(self, refresh_token: str):
        await self._key_value_session.delete(f"{KeyPrefix.REFRESH_TOKEN}:{refresh_token}")

    async def refresh_tokens(self, user_id: str) -> RefreshTokenData:
        access_token = generate_token()
        refresh_token = generate_token()

        await self._key_value_session.set(
            f"{KeyPrefix.USER_REFRESH_TOKEN}:{user_id}", refresh_token, ex=refresh_token_expiration_seconds
        )
        await self._key_value_session.set(
            f"{KeyPrefix.REFRESH_TOKEN}:{refresh_token}", user_id, ex=refresh_token_expiration_seconds
        )
        await self._key_value_session.set(
            f"{KeyPrefix.ACCESS_TOKEN}:{access_token}", user_id, ex=access_token_expiration_seconds
        )

        return RefreshTokenData(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=access_token_expiration_seconds,
            token_type=TokenType.BEARER,
        )


class EmailTokenVerifier:
    def __init__(self, key_value_repo: Redis, token: str):
        self._key_value_repo = key_value_repo
        self._email_verification_key = f"{KeyPrefix.EMAIL_VERIFICATION_TOKEN}:{token}"

    async def get_user_id_by_token(self) -> Optional[str]:
        user_id = await self._key_value_repo.get(self._email_verification_key)
        return user_id

    async def invalidate_token(self):
        await self._key_value_repo.delete(self._email_verification_key)

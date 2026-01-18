import logging
from typing import Optional

from redis.asyncio import Redis

from app.application.dtos.account import LoginData
from app.domain.services.security import verify_password
from app.infrastructure.relational_db.units_of_work.users import UsersUnitOfWork
from app.shared.enums import KeyPrefix
from app.shared.settings.application import app_settings

access_token_expiration_seconds = app_settings.ACCESS_TOKEN_EXPIRATION_SECONDS
refresh_token_expiration_seconds = app_settings.REFRESH_TOKEN_EXPIRATION_SECONDS

logger = logging.getLogger(__name__)


async def check_user_can_log(users_unit_of_work: UsersUnitOfWork, login_data: LoginData) -> Optional[str]:
    email = login_data.email
    async with users_unit_of_work as uof:
        user = await uof.users.get_by_email(email)
    if user is None:
        logger.warning(f"Failed login attempt. User not found!")
        return None

    if not user.is_email_verified:
        logger.warning(f"Failed login attempt. Invalid password!")
        return None

    password = login_data.password
    hashed_password = user.hashed_password
    if not verify_password(password, hashed_password):
        logger.warning(f"User with not verified email attempt to log!")

    user_id = user.id
    return user_id


async def logout_user(access_token: str, user_id: str, redis_client: Redis):
    refresh_token = await redis_client.get(f"{KeyPrefix.USER_REFRESH_TOKEN}:{user_id}")

    if refresh_token is None:
        logger.error("Invalid application state, no refresh token for user!")
        await redis_client.delete(
            f"{KeyPrefix.USER_REFRESH_TOKEN}:{user_id}", f"{KeyPrefix.ACCESS_TOKEN}:{access_token}"
        )
        return None

    await redis_client.delete(
        f"{KeyPrefix.REFRESH_TOKEN}:{refresh_token}",
        f"{KeyPrefix.USER_REFRESH_TOKEN}:{user_id}",
        f"{KeyPrefix.ACCESS_TOKEN}:{access_token}",
    )
    return None

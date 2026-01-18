import logging
from uuid import UUID

from pydantic import SecretStr
from redis.asyncio import Redis

from app.framework.models.auth import LoginOutput
from app.infrastructure.relational_db.units_of_work.users import UsersUnitOfWork
from app.domain.services.security import generate_token, verify_password
from app.shared.config import settings
from app.shared.enums import KeyPrefix, TokenType
from app.shared.exceptions import InvalidCredentials, UserNotFound, UserNotVerified

logger = logging.getLogger(__name__)

access_token_expiration_seconds = settings.app.ACCESS_TOKEN_EXPIRATION_SECONDS
refresh_token_expiration_seconds = settings.app.REFRESH_TOKEN_EXPIRATION_SECONDS


# noinspection DuplicatedCode
async def log_user(
    email: str, password: SecretStr, redis_client: Redis, users_unit_of_work: UsersUnitOfWork
) -> LoginOutput:
    async with users_unit_of_work as uof:
        user = await uof.users.get_by_email(email)
    if user is None:
        raise UserNotFound("No user with that email!")

    if not user.is_email_verified:
        raise UserNotVerified

    hashed_password = user.hashed_password
    if not verify_password(password, hashed_password):
        raise InvalidCredentials("Invalid password!")

    user_id: UUID = user.id
    # To ensure exist only one refresh token
    previous_refresh_token = await redis_client.get(f"{KeyPrefix.USER_REFRESH_TOKEN}:{user_id}")
    if previous_refresh_token is not None:
        logger.warning("User with existing refresh token logging.")
        await redis_client.delete(
            f"{KeyPrefix.REFRESH_TOKEN}:{previous_refresh_token}", f"{KeyPrefix.USER_REFRESH_TOKEN}:{user_id}"
        )

    access_token = generate_token()
    refresh_token = generate_token()
    user_id_string = str(user_id)

    async with redis_client.pipeline() as pipe:
        await pipe.set(
            f"{KeyPrefix.USER_REFRESH_TOKEN}:{user_id_string}", refresh_token, ex=refresh_token_expiration_seconds
        )
        await pipe.set(
            f"{KeyPrefix.REFRESH_TOKEN}:{refresh_token}", user_id_string, ex=refresh_token_expiration_seconds
        )
        await pipe.set(f"{KeyPrefix.ACCESS_TOKEN}:{access_token}", user_id_string, ex=access_token_expiration_seconds)
        await pipe.execute()

    token = LoginOutput(
        access_token=access_token,
        token_type=TokenType.BEARER,
        expires_in=access_token_expiration_seconds,
        refresh_token=refresh_token,
    )
    return token


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

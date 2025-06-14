import logging
from uuid import UUID

from pydantic import SecretStr
from redis.asyncio.client import Redis
from sqlalchemy.exc import IntegrityError

from app.config import settings
from app.core.enums import RedisPrefix, TokenType
from app.core.exceptions import InvalidCredentials, UserExists, UserNotFound
from app.core.security import generate_token, hash_password, verify_password
from app.models.account import AccountCreate, LoginOutput
from app.units_of_work.users import UsersUnitOfWork

logger = logging.getLogger(__name__)

access_token_expiration_seconds = settings.app.ACCESS_TOKEN_EXPIRATION_SECONDS
refresh_token_expiration_seconds = settings.app.REFRESH_TOKEN_EXPIRATION_SECONDS


async def create_account(users_unit_of_work: UsersUnitOfWork, account_data: AccountCreate):
    login = account_data.login
    password = account_data.password

    hashed_password = hash_password(password)
    account_hashed = {"login": login, "hashed_password": hashed_password}

    async with users_unit_of_work as uof:
        try:
            await uof.users.add(account_hashed)
        except IntegrityError:
            raise UserExists


# noinspection DuplicatedCode
async def log_user(
    login: str, password: SecretStr, redis_client: Redis, users_unit_of_work: UsersUnitOfWork
) -> LoginOutput:
    async with users_unit_of_work as uof:
        user = await uof.users.get_by_login(login)
    if user is None:
        raise UserNotFound("No user with that login!")

    hashed_password = user.hashed_password
    if not verify_password(password, hashed_password):
        raise InvalidCredentials("Invalid password!")

    user_id: UUID = user.id
    # To ensure exist only one refresh token
    previous_refresh_token = await redis_client.get(f"{RedisPrefix.USER_REFRESH_TOKEN}:{user_id}")
    if previous_refresh_token is not None:
        logger.warning("User with existing refresh token logging.")
        async with redis_client.pipeline() as pipe:
            await pipe.delete(f"{RedisPrefix.REFRESH_TOKEN}:{previous_refresh_token}")
            await pipe.delete(f"{RedisPrefix.USER_REFRESH_TOKEN}:{user_id}")
            await pipe.execute()

    access_token = generate_token()
    refresh_token = generate_token()
    user_id_string = str(user_id)

    async with redis_client.pipeline() as pipe:
        await pipe.set(
            f"{RedisPrefix.USER_REFRESH_TOKEN}:{user_id_string}", refresh_token, ex=refresh_token_expiration_seconds
        )
        await pipe.set(
            f"{RedisPrefix.REFRESH_TOKEN}:{refresh_token}", user_id_string, ex=refresh_token_expiration_seconds
        )
        await pipe.set(f"{RedisPrefix.ACCESS_TOKEN}:{access_token}", user_id_string, ex=access_token_expiration_seconds)
        await pipe.execute()

    token = LoginOutput(
        access_token=access_token,
        token_type=TokenType.BEARER,
        expires_in=access_token_expiration_seconds,
        refresh_token=refresh_token,
    )
    return token


async def logout_user(access_token: str, user_id: str, redis_client: Redis):
    refresh_token = await redis_client.get(f"{RedisPrefix.USER_REFRESH_TOKEN}:{user_id}")

    if refresh_token is None:
        logger.error("Invalid application state, no refresh token for user!")
        async with redis_client.pipeline() as pipe:
            await pipe.delete(f"{RedisPrefix.USER_REFRESH_TOKEN}:{user_id}")
            await pipe.delete(f"{RedisPrefix.ACCESS_TOKEN}:{access_token}")
            await pipe.execute()
        return None

    async with redis_client.pipeline() as pipe:
        await pipe.delete(f"{RedisPrefix.REFRESH_TOKEN}:{refresh_token}")
        await pipe.delete(f"{RedisPrefix.USER_REFRESH_TOKEN}:{user_id}")
        await pipe.delete(f"{RedisPrefix.ACCESS_TOKEN}:{access_token}")
        await pipe.execute()
    return None


# noinspection DuplicatedCode
async def refresh(refresh_token: str, redis_client: Redis) -> LoginOutput:
    user_id = await redis_client.get(f"{RedisPrefix.REFRESH_TOKEN}:{refresh_token}")
    if not user_id:
        raise InvalidCredentials()

    access_token = generate_token()
    new_refresh_token = generate_token()

    async with redis_client.pipeline() as pipe:
        await pipe.delete(f"{RedisPrefix.REFRESH_TOKEN}:{refresh_token}")
        await pipe.set(
            f"{RedisPrefix.USER_REFRESH_TOKEN}:{user_id}", new_refresh_token, ex=refresh_token_expiration_seconds
        )
        await pipe.set(f"{RedisPrefix.REFRESH_TOKEN}:{new_refresh_token}", user_id, ex=refresh_token_expiration_seconds)
        await pipe.set(f"{RedisPrefix.ACCESS_TOKEN}:{access_token}", user_id, ex=access_token_expiration_seconds)
        await pipe.execute()

    return LoginOutput(
        access_token=access_token,
        refresh_token=new_refresh_token,
        expires_in=access_token_expiration_seconds,
        token_type=TokenType.BEARER,
    )

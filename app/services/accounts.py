import logging

from sqlalchemy.exc import IntegrityError
from redis.asyncio.client import Redis

from app.models.account import AccountCreate, LoginOutput
from app.core.security import hash_password, verify_password, generate_token
from app.core.exceptions import UserExists, InvalidCredentials, UserNotFound
from app.units_of_work.users import UsersUnitOfWork
from app.core.enums import TokenType
from app.config import settings


logger = logging.getLogger(__name__)

access_token_expiration_seconds = settings.app.ACCESS_TOKEN_EXPIRATION_SECONDS
refresh_token_expiration_seconds = settings.app.REFRESH_TOKEN_EXPIRATION_SECONDS


async def create_account(users_unit_of_work: UsersUnitOfWork, account_data: AccountCreate):
    login = account_data.login
    password = account_data.password

    hashed_password = hash_password(password)
    account_hashed = {"login": login, "hashed_password": hashed_password}

    try:
        async with users_unit_of_work as uof:
            await uof.users.add(account_hashed)
    except IntegrityError:
        raise UserExists


async def log_user(login: str, password: str, redis_client: Redis, users_unit_of_work: UsersUnitOfWork) -> LoginOutput:
    async with users_unit_of_work as uof:
        user = await uof.users.get_by_login(login)
    if user is None:
        verify_password(password, b'') # To prevent timeing attacks
        raise UserNotFound('No user with that login!')

    hashed_password = user.hashed_password
    if not verify_password(password, hashed_password):
        raise InvalidCredentials('Invalid password!')

    user_id = user.id
    # To ensure exist only one refresh token
    previous_refresh_token = await redis_client.get(f"user_refresh_token:{user_id}")
    if previous_refresh_token is not None:
        logger.warning('User with existing refresh token logging.')
        async with redis_client.pipeline() as pipe:
            await pipe.delete(f'refresh_token:{previous_refresh_token}')
            await pipe.delete(f"user_refresh_token:{user_id}")
            await pipe.execute()

    access_token = generate_token()
    refresh_token = generate_token()
    user_id_string = str(user_id)

    async with redis_client.pipeline() as pipe:
        await pipe.set(f"user_refresh_token:{user_id_string}", refresh_token, ex=refresh_token_expiration_seconds)
        await pipe.set(f'refresh_token:{refresh_token}', user_id_string, ex=refresh_token_expiration_seconds)
        await pipe.set(f'access_token:{access_token}', user_id_string, ex=access_token_expiration_seconds)
        await pipe.execute()

    token = LoginOutput(access_token=access_token,
                        token_type=TokenType.bearer,
                        expires_in=access_token_expiration_seconds,
                        refresh_token=refresh_token)
    return token

from unittest.mock import AsyncMock, patch

import pytest
from pydantic import SecretStr
from sqlalchemy.exc import IntegrityError

from app.config import settings
from app.core.enums import TokenType
from app.core.exceptions import InvalidCredentials, UserExists, UserNotFound
from app.models.account import AccountCreate, LoginOutput
from app.services.accounts import create_account, log_user, logout_user, refresh
from tests.test_consts import STRONG_PASSWORD

ACCESS_TOKEN_EXPIRATION_SECONDS = settings.app.ACCESS_TOKEN_EXPIRATION_SECONDS
REFRESH_TOKEN_EXPIRATION_SECONDS = settings.app.REFRESH_TOKEN_EXPIRATION_SECONDS


@pytest.fixture
def mock_hash_password():
    with patch("app.services.accounts.verify_password", return_value=True) as mock:
        yield mock


@pytest.mark.asyncio
async def test_create_account_success(uow):
    strong_password = SecretStr(STRONG_PASSWORD)
    account_data = AccountCreate(login="valid_user", password=strong_password)
    uow.users.add = AsyncMock()

    with patch("app.services.accounts.hash_password", return_value=b"hashed_pass") as mock_hash:
        await create_account(uow, account_data)

    mock_hash.assert_called_once_with(strong_password)
    uow.users.add.assert_awaited_once_with({"login": "valid_user", "hashed_password": b"hashed_pass"})


@pytest.mark.asyncio
async def test_create_account_user_exists(uow):
    strong_password = SecretStr(STRONG_PASSWORD)
    account_data = AccountCreate(login="already_taken", password=strong_password)
    uow.users.add = AsyncMock(side_effect=IntegrityError("msg", None, Exception()))

    with patch("app.services.accounts.hash_password", return_value=b"hashed_pass"):
        with pytest.raises(UserExists):
            await create_account(uow, account_data)


@pytest.mark.asyncio
async def test_create_account_hashing_and_argument_check(uow):
    strong_password = SecretStr(STRONG_PASSWORD)
    account_data = AccountCreate(login="test_user", password=strong_password)
    uow.users.add = AsyncMock()

    with patch("app.services.accounts.hash_password", return_value=b"hashed") as mock_hash:
        await create_account(uow, account_data)
        mock_hash.assert_called_once_with(strong_password)
        uow.users.add.assert_awaited_once_with({"login": "test_user", "hashed_password": b"hashed"})


@pytest.mark.asyncio
async def test_log_user_success(user, uow, redis_client, mock_hash_password, bearer_token_generator):
    redis, _ = redis_client
    correct_password = SecretStr(STRONG_PASSWORD)
    access_token = next(bearer_token_generator)
    refresh_token = next(bearer_token_generator)

    with (
        patch("app.services.accounts.LoginOutput") as mock_login_output,
        patch("app.services.accounts.generate_token", side_effect=[access_token, refresh_token]),
    ):
        await log_user("test_user", correct_password, redis, uow)
    mock_login_output.assert_called_once()
    called_kwargs = mock_login_output.call_args.kwargs
    assert called_kwargs["access_token"] == access_token
    assert called_kwargs["refresh_token"] == refresh_token


@pytest.mark.asyncio
async def test_log_user_invalid_password(user, uow, redis_client):
    redis, _ = redis_client
    wrong_password = SecretStr(STRONG_PASSWORD)
    with patch("app.services.accounts.verify_password", return_value=False):
        with pytest.raises(InvalidCredentials):
            await log_user("test_user", wrong_password, redis, uow)


@pytest.mark.asyncio
async def test_log_user_user_not_found(uow, redis_client):
    redis, _ = redis_client
    strong_password = SecretStr(STRONG_PASSWORD)
    uow.users.get_by_login = AsyncMock(return_value=None)
    with patch("app.services.accounts.verify_password", return_value=False):
        with pytest.raises(UserNotFound):
            await log_user("not_existing_user", strong_password, redis, uow)


@pytest.mark.asyncio
async def test_log_user_existing_refresh_token(user, uow, redis_client, mock_hash_password, bearer_token_generator):
    redis, pipeline = redis_client
    strong_password = SecretStr(STRONG_PASSWORD)
    refresh_token = next(bearer_token_generator)
    redis.get = AsyncMock(return_value=refresh_token)
    uow.users.get_by_login = AsyncMock(return_value=user)

    await log_user("test_user", strong_password, redis, uow)
    pipeline.delete.assert_any_call(f"refresh_token:{refresh_token}")
    pipeline.delete.assert_any_call(f"user_refresh_token:{str(user.id)}")
    pipeline.execute.assert_awaited()


@pytest.mark.asyncio
async def test_log_user_no_existing_refresh_token(user, uow, redis_client, mock_hash_password):
    redis, pipeline = redis_client
    strong_password = SecretStr(STRONG_PASSWORD)
    redis.get = AsyncMock(return_value=None)
    await log_user("test_user", strong_password, redis, uow)
    pipeline.delete.assert_not_called()


@pytest.mark.asyncio
async def test_logout_user_success(redis_client, bearer_token_generator, uuid_generator):
    redis, pipeline = redis_client
    access_token = next(bearer_token_generator)
    refresh_token = next(bearer_token_generator)
    user_id = next(uuid_generator)
    redis.get = AsyncMock(return_value=refresh_token)

    result = await logout_user(access_token, user_id, redis)

    redis.get.assert_awaited_once_with(f"user_refresh_token:{user_id}")
    pipeline.delete.assert_any_await(f"refresh_token:{refresh_token}")
    pipeline.delete.assert_any_await(f"user_refresh_token:{user_id}")
    pipeline.delete.assert_any_await(f"access_token:{access_token}")
    pipeline.execute.assert_awaited_once()
    assert result is None


@pytest.mark.asyncio
async def test_logout_user_no_refresh_token(redis_client, bearer_token_generator, uuid_generator):
    redis, pipeline = redis_client
    user_id = next(uuid_generator)
    access_token = next(bearer_token_generator)

    await logout_user(access_token, user_id, redis)

    redis.get.assert_awaited_once_with(f"user_refresh_token:{user_id}")
    pipeline.delete.assert_any_await(f"user_refresh_token:{user_id}")
    pipeline.delete.assert_any_await(f"access_token:{access_token}")
    pipeline.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_refresh_success(redis_client, bearer_token_generator, uuid_generator):
    redis, pipeline = redis_client
    user_id = next(uuid_generator)
    redis.get = AsyncMock(return_value=user_id)

    access_token = next(bearer_token_generator)
    refresh_token = next(bearer_token_generator)
    new_refresh_token = next(bearer_token_generator)

    with patch("app.services.accounts.generate_token", side_effect=[access_token, new_refresh_token]):
        result = await refresh(refresh_token, redis)

    redis.get.assert_awaited_once_with(f"refresh_token:{refresh_token}")
    pipeline.delete.assert_any_await(f"refresh_token:{refresh_token}")
    pipeline.set.assert_any_await(
        f"user_refresh_token:{user_id}", new_refresh_token, ex=REFRESH_TOKEN_EXPIRATION_SECONDS
    )
    pipeline.set.assert_any_await(f"refresh_token:{new_refresh_token}", user_id, ex=REFRESH_TOKEN_EXPIRATION_SECONDS)
    pipeline.set.assert_any_await(f"access_token:{access_token}", user_id, ex=ACCESS_TOKEN_EXPIRATION_SECONDS)
    pipeline.execute.assert_awaited_once()

    assert isinstance(result, LoginOutput)
    assert result.access_token == access_token
    assert result.refresh_token == new_refresh_token
    assert result.expires_in == ACCESS_TOKEN_EXPIRATION_SECONDS
    assert result.token_type == TokenType.BEARER


@pytest.mark.asyncio
async def test_refresh_invalid_refresh_token(redis_client, bearer_token_generator):
    redis, _ = redis_client
    not_existing_token = next(bearer_token_generator)
    redis.get = AsyncMock(return_value=None)

    with pytest.raises(InvalidCredentials):
        await refresh(not_existing_token, redis)
    redis.get.assert_awaited_once_with(f"refresh_token:{not_existing_token}")


@pytest.mark.asyncio
async def test_refresh_redis_user_not_found(redis_client, bearer_token_generator):
    redis, _ = redis_client
    expired_token = next(bearer_token_generator)
    redis.get = AsyncMock(return_value=None)

    with pytest.raises(InvalidCredentials):
        await refresh(expired_token, redis)
    redis.get.assert_awaited_once_with(f"refresh_token:{expired_token}")

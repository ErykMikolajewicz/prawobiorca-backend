from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import InvalidCredentials, UserNotFound, UserExists
from app.services.accounts import log_user, create_account, logout_user, refresh
from app.models.account import AccountCreate, LoginOutput
from app.core.enums import TokenType
from tests.unit.consts import valid_bearer_token, user_id, access_token_expiration_seconds, \
    refresh_token_expiration_seconds


@pytest.fixture
def token_mocks():
    with patch("app.services.accounts.generate_token", side_effect=["access", "refresh"]) as mock_gen, \
         patch("app.services.accounts.verify_password", return_value=True) as mock_ver, \
         patch("app.services.accounts.LoginOutput") as mock_out, \
         patch("app.services.accounts.TokenType") as mock_type, \
         patch("app.services.accounts.access_token_expiration_seconds", 3600), \
         patch("app.services.accounts.refresh_token_expiration_seconds", 7200):
        yield mock_gen, mock_ver, mock_out, mock_type


@pytest.mark.asyncio
async def test_create_account_success(uow):
    account_data = AccountCreate(login="valid_user", password="Valid123!")
    uow.users.add = AsyncMock()

    with patch("app.services.accounts.hash_password", return_value=b"hashed_pass") as mock_hash:
        await create_account(uow, account_data)

    mock_hash.assert_called_once_with("Valid123!")
    uow.users.add.assert_awaited_once_with({
        "login": "valid_user",
        "hashed_password": b"hashed_pass"
    })


@pytest.mark.asyncio
async def test_create_account_user_exists(uow):
    account_data = AccountCreate(login="already_taken", password="Valid123!")
    uow.users.add = AsyncMock(side_effect=IntegrityError("msg", None, Exception()))

    with patch("app.services.accounts.hash_password", return_value=b"hashed_pass"):
        with pytest.raises(UserExists):
            await create_account(uow, account_data)


@pytest.mark.asyncio
async def test_create_account_hashing_and_argument_check(uow):
    account_data = AccountCreate(login="test_user", password="Valid123!")
    uow.users.add = AsyncMock()

    with patch("app.services.accounts.hash_password", return_value=b"hashed") as mock_hash:
        await create_account(uow, account_data)
        mock_hash.assert_called_once_with("Valid123!")
        uow.users.add.assert_awaited_once_with({
            "login": "test_user",
            "hashed_password": b"hashed"
        })


@pytest.mark.asyncio
async def test_log_user_success(user, uow, redis_client, token_mocks):
    redis, _ = redis_client
    await log_user("test_user", "secret", redis, uow)
    token_mocks[2].assert_called_once()
    called_kwargs = token_mocks[2].call_args.kwargs
    assert called_kwargs["access_token"] == "access"
    assert called_kwargs["refresh_token"] == "refresh"


@pytest.mark.asyncio
async def test_log_user_invalid_password(user, uow, redis_client):
    redis, _ = redis_client
    with patch("app.services.accounts.verify_password", return_value=False):
        with pytest.raises(InvalidCredentials):
            await log_user("test_user", "wrong_pass", redis, uow)


@pytest.mark.asyncio
async def test_log_user_user_not_found(uow, redis_client):
    redis, _ = redis_client
    uow.users.get_by_login = AsyncMock(return_value=None)
    with patch("app.services.accounts.verify_password", return_value=False):
        with pytest.raises(UserNotFound):
            await log_user("noone", "pass", redis, uow)


@pytest.mark.asyncio
async def test_log_user_existing_refresh_token(user, uow, redis_client, token_mocks):
    redis, pipeline = redis_client
    redis.get = AsyncMock(return_value="old_refresh")
    uow.users.get_by_login = AsyncMock(return_value=user)
    await log_user("test_user", "secret", redis, uow)
    pipeline.delete.assert_any_call("refresh_token:old_refresh")
    pipeline.delete.assert_any_call(f"user_refresh_token:{str(user.id)}")
    pipeline.execute.assert_awaited()


@pytest.mark.asyncio
async def test_log_user_no_existing_refresh_token(user, uow, redis_client, token_mocks):
    redis, pipeline = redis_client
    redis.get = AsyncMock(return_value=None)
    await log_user("test_user", "secret", redis, uow)
    pipeline.delete.assert_not_called()


@pytest.mark.asyncio
async def test_logout_user_success(redis_client):
    redis, pipeline = redis_client
    redis.get = AsyncMock(return_value="refresh-token-abc")

    access_token = "token-access"

    result = await logout_user(access_token, user_id, redis)

    redis.get.assert_awaited_once_with(f"user_refresh_token:{user_id}")
    pipeline.delete.assert_any_await(f'refresh_token:refresh-token-abc')
    pipeline.delete.assert_any_await(f"user_refresh_token:{user_id}")
    pipeline.delete.assert_any_await(f'access_token:{access_token}')
    pipeline.execute.assert_awaited_once()
    assert result is None

@pytest.mark.asyncio
async def test_logout_user_no_refresh_token(redis_client):
    redis, pipeline = redis_client

    access_token = "token-access"

    await logout_user(access_token, user_id, redis)

    redis.get.assert_awaited_once_with(f"user_refresh_token:{user_id}")
    pipeline.delete.assert_any_await(f"user_refresh_token:{user_id}")
    pipeline.delete.assert_any_await(f'access_token:{access_token}')
    pipeline.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_refresh_success(redis_client):
    redis, pipeline = redis_client
    redis.get = AsyncMock(return_value=user_id)

    access_token = valid_bearer_token
    new_refresh_token = valid_bearer_token

    with patch("app.services.accounts.generate_token", side_effect=[access_token, new_refresh_token]):

        result = await refresh("refresh_token_example", redis)

    redis.get.assert_awaited_once_with("refresh_token:refresh_token_example")
    pipeline.delete.assert_any_await("refresh_token:refresh_token_example")
    pipeline.set.assert_any_await(f"user_refresh_token:{user_id}", new_refresh_token,
                                  ex=refresh_token_expiration_seconds)
    pipeline.set.assert_any_await(f"refresh_token:{new_refresh_token}", user_id, ex=refresh_token_expiration_seconds)
    pipeline.set.assert_any_await(f"access_token:{access_token}", user_id, ex=access_token_expiration_seconds)
    pipeline.execute.assert_awaited_once()

    assert isinstance(result, LoginOutput)
    assert result.access_token == access_token
    assert result.refresh_token == new_refresh_token
    assert result.expires_in == access_token_expiration_seconds
    assert result.token_type == TokenType.bearer


@pytest.mark.asyncio
async def test_refresh_invalid_refresh_token(redis_client):
    redis, _ = redis_client
    redis.get = AsyncMock(return_value=None)

    with pytest.raises(InvalidCredentials):
        await refresh("not_existing_token", redis)
    redis.get.assert_awaited_once_with("refresh_token:not_existing_token")


@pytest.mark.asyncio
async def test_refresh_redis_returns_empty_string(redis_client):
    redis, _ = redis_client
    redis.get = AsyncMock(return_value="")

    with pytest.raises(InvalidCredentials):
        await refresh("expired_token", redis)
    redis.get.assert_awaited_once_with("refresh_token:expired_token")

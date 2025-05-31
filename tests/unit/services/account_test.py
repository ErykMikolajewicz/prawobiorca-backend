import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from app.core.exceptions import InvalidCredentials, UserNotFound
from app.services.accounts import log_user


class DummyUser:
    def __init__(self, id_, login, hashed_password):
        self.id = id_
        self.login = login
        self.hashed_password = hashed_password


@pytest.fixture
def user():
    return DummyUser(id_=uuid4(), login="testuser", hashed_password=b"hashed")


@pytest.fixture
def uow(user):
    uow = AsyncMock()
    uow.__aenter__.return_value = uow
    uow.users.get_by_login = AsyncMock(return_value=user)
    return uow


@pytest.fixture
def uow_none():
    uow = AsyncMock()
    uow.__aenter__.return_value = uow
    uow.users.get_by_login = AsyncMock(return_value=None)
    return uow


@pytest.fixture
def redis_client():
    redis = AsyncMock()
    redis.get = AsyncMock(return_value=None)
    pipeline = AsyncMock()

    class DummyAsyncContextManager:
        async def __aenter__(self):
            return pipeline
        async def __aexit__(self, exc_type, exc, tb):
            return None

    redis.pipeline = lambda: DummyAsyncContextManager()
    return redis, pipeline


@pytest.fixture
def redis_client_with_token():
    redis = AsyncMock()
    redis.get = AsyncMock(return_value="old_refresh")
    pipeline = AsyncMock()

    class DummyAsyncContextManager:
        async def __aenter__(self):
            return pipeline
        async def __aexit__(self, exc_type, exc, tb):
            return None

    redis.pipeline = lambda: DummyAsyncContextManager()
    return redis, pipeline


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
async def test_log_user_success(user, uow, redis_client, token_mocks):
    redis, _ = redis_client
    result = await log_user("testuser", "secret", redis, uow)
    token_mocks[2].assert_called_once()
    called_kwargs = token_mocks[2].call_args.kwargs
    assert called_kwargs["access_token"] == "access"
    assert called_kwargs["refresh_token"] == "refresh"


@pytest.mark.asyncio
async def test_log_user_invalid_password(user, uow, redis_client):
    redis, _ = redis_client
    with patch("app.services.accounts.verify_password", return_value=False):
        with pytest.raises(InvalidCredentials):
            await log_user("testuser", "wrongpass", redis, uow)


@pytest.mark.asyncio
async def test_log_user_user_not_found(uow_none, redis_client):
    redis, _ = redis_client
    with patch("app.services.accounts.verify_password", return_value=False) as mock_ver:
        with pytest.raises(UserNotFound):
            await log_user("noone", "pass", redis, uow_none)
        mock_ver.assert_called_once_with("pass", b"")


@pytest.mark.asyncio
async def test_log_user_existing_refresh_token(user, uow, redis_client_with_token, token_mocks):
    redis, pipeline = redis_client_with_token
    await log_user("testuser", "secret", redis, uow)
    pipeline.delete.assert_any_call("refresh_token:old_refresh")
    pipeline.delete.assert_any_call(f"user_refresh_token:{str(user.id)}")
    pipeline.execute.assert_awaited()


@pytest.mark.asyncio
async def test_log_user_no_existing_refresh_token(user, uow, redis_client, token_mocks):
    redis, pipeline = redis_client
    await log_user("testuser", "secret", redis, uow)
    pipeline.delete.assert_not_called()

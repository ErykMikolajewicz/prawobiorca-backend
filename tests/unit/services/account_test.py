from unittest.mock import AsyncMock, patch

import pytest
from pydantic import SecretStr
from sqlalchemy.exc import IntegrityError

from app.config import settings
from app.shared.enums import KeyPrefix, TokenType
from app.shared.exceptions import InvalidCredentials, UserExists, UserNotFound
from app.domain.models.account import AccountCreate, LoginOutput
from app.domain.services.accounts import create_account, log_user, logout_user, refresh
from tests.test_consts import STRONG_PASSWORD


ACCESS_TOKEN_EXPIRATION_SECONDS = settings.app.ACCESS_TOKEN_EXPIRATION_SECONDS
REFRESH_TOKEN_EXPIRATION_SECONDS = settings.app.REFRESH_TOKEN_EXPIRATION_SECONDS


@pytest.fixture
def mock_hash_password():
    with patch("app.domain.services.accounts.verify_password", return_value=True) as mock:
        yield mock


async def test_create_account_success(uow):
    strong_password = SecretStr(STRONG_PASSWORD)
    account_data = AccountCreate(login="valid_user", password=strong_password)
    uow.users.add = AsyncMock()

    with patch("app.domain.services.accounts.hash_password", return_value=b"hashed_pass") as mock_hash:
        await create_account(uow, account_data)

    mock_hash.assert_called_once_with(strong_password)
    uow.users.add.assert_awaited_once_with({"login": "valid_user", "hashed_password": b"hashed_pass"})


async def test_create_account_user_exists(uow):
    strong_password = SecretStr(STRONG_PASSWORD)
    account_data = AccountCreate(login="already_taken", password=strong_password)
    uow.users.add = AsyncMock(side_effect=IntegrityError("msg", None, Exception()))

    with patch("app.domain.services.accounts.hash_password", return_value=b"hashed_pass"):
        with pytest.raises(UserExists):
            await create_account(uow, account_data)


async def test_create_account_hashing_and_argument_check(uow):
    strong_password = SecretStr(STRONG_PASSWORD)
    account_data = AccountCreate(login="test_user", password=strong_password)
    uow.users.add = AsyncMock()

    with patch("app.domain.services.accounts.hash_password", return_value=b"hashed") as mock_hash:
        await create_account(uow, account_data)
        mock_hash.assert_called_once_with(strong_password)
        uow.users.add.assert_awaited_once_with({"login": "test_user", "hashed_password": b"hashed"})


async def test_log_user_success(user, uow, key_value_repository, mock_hash_password, bearer_token_generator):
    key_value_repository, _ = key_value_repository
    correct_password = SecretStr(STRONG_PASSWORD)
    access_token = next(bearer_token_generator)
    refresh_token = next(bearer_token_generator)

    with (
        patch("app.domain.services.accounts.LoginOutput") as mock_login_output,
        patch("app.domain.services.accounts.generate_token", side_effect=[access_token, refresh_token]),
    ):
        await log_user("test_user", correct_password, key_value_repository, uow)
    mock_login_output.assert_called_once()
    called_kwargs = mock_login_output.call_args.kwargs
    assert called_kwargs["access_token"] == access_token
    assert called_kwargs["refresh_token"] == refresh_token


async def test_log_user_invalid_password(user, uow, key_value_repository):
    key_value_repository, _ = key_value_repository
    wrong_password = SecretStr(STRONG_PASSWORD)
    with patch("app.domain.services.accounts.verify_password", return_value=False):
        with pytest.raises(InvalidCredentials):
            await log_user("test_user", wrong_password, key_value_repository, uow)


async def test_log_user_user_not_found(uow, key_value_repository):
    key_value_repository, _ = key_value_repository
    strong_password = SecretStr(STRONG_PASSWORD)
    uow.users.get_by_login = AsyncMock(return_value=None)
    with patch("app.domain.services.accounts.verify_password", return_value=False):
        with pytest.raises(UserNotFound):
            await log_user("not_existing_user", strong_password, key_value_repository, uow)


async def test_log_user_existing_refresh_token(user, uow, key_value_repository, mock_hash_password, bearer_token_generator):
    key_value_repository, pipeline = key_value_repository
    strong_password = SecretStr(STRONG_PASSWORD)
    refresh_token = next(bearer_token_generator)
    key_value_repository.get = AsyncMock(return_value=refresh_token)
    uow.users.get_by_login = AsyncMock(return_value=user)

    await log_user("test_user", strong_password, key_value_repository, uow)
    pipeline.delete.assert_any_call(f"{KeyPrefix.REFRESH_TOKEN}:{refresh_token}")
    pipeline.delete.assert_any_call(f"{KeyPrefix.USER_REFRESH_TOKEN}:{str(user.id)}")
    pipeline.execute.assert_awaited()


async def test_log_user_no_existing_refresh_token(user, uow, key_value_repository, mock_hash_password):
    key_value_repository, pipeline = key_value_repository
    strong_password = SecretStr(STRONG_PASSWORD)
    key_value_repository.get = AsyncMock(return_value=None)
    await log_user("test_user", strong_password, key_value_repository, uow)
    pipeline.delete.assert_not_called()


async def test_logout_user_success(key_value_repository, bearer_token_generator, uuid_generator):
    key_value_repository, pipeline = key_value_repository
    access_token = next(bearer_token_generator)
    refresh_token = next(bearer_token_generator)
    user_id = next(uuid_generator)
    key_value_repository.get = AsyncMock(return_value=refresh_token)

    result = await logout_user(access_token, user_id, key_value_repository)

    key_value_repository.get.assert_awaited_once_with(f"{KeyPrefix.USER_REFRESH_TOKEN}:{user_id}")
    pipeline.delete.assert_any_await(f"{KeyPrefix.REFRESH_TOKEN}:{refresh_token}")
    pipeline.delete.assert_any_await(f"{KeyPrefix.USER_REFRESH_TOKEN}:{user_id}")
    pipeline.delete.assert_any_await(f"{KeyPrefix.ACCESS_TOKEN}:{access_token}")
    pipeline.execute.assert_awaited_once()
    assert result is None


async def test_logout_user_no_refresh_token(key_value_repository, bearer_token_generator, uuid_generator):
    key_value_repository, pipeline = key_value_repository
    user_id = next(uuid_generator)
    access_token = next(bearer_token_generator)

    await logout_user(access_token, user_id, key_value_repository)

    key_value_repository.get.assert_awaited_once_with(f"{KeyPrefix.USER_REFRESH_TOKEN}:{user_id}")
    pipeline.delete.assert_any_await(f"{KeyPrefix.USER_REFRESH_TOKEN}:{user_id}")
    pipeline.delete.assert_any_await(f"{KeyPrefix.ACCESS_TOKEN}:{access_token}")
    pipeline.execute.assert_awaited_once()


async def test_refresh_success(key_value_repository, bearer_token_generator, uuid_generator):
    key_value_repository, pipeline = key_value_repository
    user_id = next(uuid_generator)
    key_value_repository.get = AsyncMock(return_value=user_id)

    access_token = next(bearer_token_generator)
    refresh_token = next(bearer_token_generator)
    new_refresh_token = next(bearer_token_generator)

    with patch("app.domain.services.accounts.generate_token", side_effect=[access_token, new_refresh_token]):
        result = await refresh(refresh_token, key_value_repository)

    key_value_repository.get.assert_awaited_once_with(f"{KeyPrefix.REFRESH_TOKEN}:{refresh_token}")
    pipeline.delete.assert_any_await(f"{KeyPrefix.REFRESH_TOKEN}:{refresh_token}")
    pipeline.set.assert_any_await(
        f"{KeyPrefix.USER_REFRESH_TOKEN}:{user_id}", new_refresh_token, ex=REFRESH_TOKEN_EXPIRATION_SECONDS
    )
    pipeline.set.assert_any_await(
        f"{KeyPrefix.REFRESH_TOKEN}:{new_refresh_token}", user_id, ex=REFRESH_TOKEN_EXPIRATION_SECONDS
    )
    pipeline.set.assert_any_await(
        f"{KeyPrefix.ACCESS_TOKEN}:{access_token}", user_id, ex=ACCESS_TOKEN_EXPIRATION_SECONDS
    )
    pipeline.execute.assert_awaited_once()

    assert isinstance(result, LoginOutput)
    assert result.access_token == access_token
    assert result.refresh_token == new_refresh_token
    assert result.expires_in == ACCESS_TOKEN_EXPIRATION_SECONDS
    assert result.token_type == TokenType.BEARER


async def test_refresh_invalid_refresh_token(key_value_repository, bearer_token_generator):
    key_value_repository, _ = key_value_repository
    not_existing_token = next(bearer_token_generator)
    key_value_repository.get = AsyncMock(return_value=None)

    with pytest.raises(InvalidCredentials):
        await refresh(not_existing_token, key_value_repository)
    key_value_repository.get.assert_awaited_once_with(f"{KeyPrefix.REFRESH_TOKEN}:{not_existing_token}")


async def test_refresh_user_not_found(key_value_repository, bearer_token_generator):
    key_value_repository, _ = key_value_repository
    expired_token = next(bearer_token_generator)
    key_value_repository.get = AsyncMock(return_value=None)

    with pytest.raises(InvalidCredentials):
        await refresh(expired_token, key_value_repository)
    key_value_repository.get.assert_awaited_once_with(f"{KeyPrefix.REFRESH_TOKEN}:{expired_token}")

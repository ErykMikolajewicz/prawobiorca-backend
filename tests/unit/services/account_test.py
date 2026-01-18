from typing import cast
from unittest.mock import AsyncMock, patch

import pytest
from pydantic import EmailStr, SecretStr
from sqlalchemy.exc import IntegrityError

from app.domain.models.account import AccountCreate, LoginOutput
from app.domain.services.accounts import create_account, log_user, logout_user, refresh, verify_account_email
from app.shared.config import settings
from app.shared.enums import KeyPrefix, TokenType
from app.shared.exceptions import InvalidCredentials, UserExists, UserNotFound
from tests.test_consts import STRONG_PASSWORD, VALID_EMAIL
from tests.unit.services.conftest import key_value_repository

ACCESS_TOKEN_EXPIRATION_SECONDS = settings.app.ACCESS_TOKEN_EXPIRATION_SECONDS
REFRESH_TOKEN_EXPIRATION_SECONDS = settings.app.REFRESH_TOKEN_EXPIRATION_SECONDS


@pytest.fixture
def mock_hash_password():
    with patch("app.domain.services.accounts.verify_password", return_value=True) as mock:
        yield mock


async def test_create_account_success(uow):
    strong_password = SecretStr(STRONG_PASSWORD)
    email = cast(EmailStr, VALID_EMAIL)
    account_data = AccountCreate(email=email, password=strong_password)
    uow.users.add = AsyncMock()

    with patch("app.domain.services.accounts.hash_password", return_value=b"hashed_pass") as mock_hash:
        await create_account(uow, account_data)

    mock_hash.assert_called_once_with(strong_password)
    uow.users.add.assert_awaited_once_with({"email": email, "hashed_password": b"hashed_pass"})
    uow.commit.assert_awaited_once()


async def test_create_account_user_exists(uow):
    strong_password = SecretStr(STRONG_PASSWORD)
    taken_email = cast(EmailStr, VALID_EMAIL)
    account_data = AccountCreate(email=taken_email, password=strong_password)
    uow.users.add = AsyncMock(side_effect=IntegrityError("msg", None, Exception()))

    with patch("app.domain.services.accounts.hash_password", return_value=b"hashed_pass"):
        with pytest.raises(UserExists):
            await create_account(uow, account_data)
    uow.commit.assert_not_awaited()


async def test_create_account_hashing_and_argument_check(uow):
    strong_password = SecretStr(STRONG_PASSWORD)
    email = cast(EmailStr, VALID_EMAIL)
    account_data = AccountCreate(email=email, password=strong_password)
    uow.users.add = AsyncMock()

    with patch("app.domain.services.accounts.hash_password", return_value=b"hashed") as mock_hash:
        await create_account(uow, account_data)
    mock_hash.assert_called_once_with(strong_password)
    uow.users.add.assert_awaited_once_with({"email": email, "hashed_password": b"hashed"})
    uow.commit.assert_awaited_once()


async def test_log_user_success(user, uow, key_value_repository, mock_hash_password, bearer_token_generator):
    redis_client, _ = key_value_repository
    correct_password = SecretStr(STRONG_PASSWORD)
    access_token = next(bearer_token_generator)
    refresh_token = next(bearer_token_generator)

    with (
        patch("app.domain.services.accounts.LoginOutput") as mock_login_output,
        patch("app.domain.services.accounts.generate_token", side_effect=[access_token, refresh_token]),
    ):
        await log_user(VALID_EMAIL, correct_password, redis_client, uow)
    mock_login_output.assert_called_once()
    called_kwargs = mock_login_output.call_args.kwargs
    assert called_kwargs["access_token"] == access_token
    assert called_kwargs["refresh_token"] == refresh_token
    uow.commit.assert_awaited_once()


async def test_log_user_invalid_password(user, uow, key_value_repository):
    redis_client, _ = key_value_repository
    wrong_password = SecretStr(STRONG_PASSWORD)
    with patch("app.domain.services.accounts.verify_password", return_value=False):
        with pytest.raises(InvalidCredentials):
            await log_user(VALID_EMAIL, wrong_password, redis_client, uow)
    uow.commit.assert_awaited_once()


async def test_log_user_user_not_found(uow, key_value_repository):
    redis_client, _ = key_value_repository
    strong_password = SecretStr(STRONG_PASSWORD)
    email_without_user = VALID_EMAIL
    uow.users.get_by_email = AsyncMock(return_value=None)
    with patch("app.domain.services.accounts.verify_password", return_value=False):
        with pytest.raises(UserNotFound):
            await log_user(email_without_user, strong_password, redis_client, uow)
    uow.commit.assert_awaited_once()


async def test_log_user_existing_refresh_token(
    user, uow, key_value_repository, mock_hash_password, bearer_token_generator
):
    redis_client, pipeline = key_value_repository
    strong_password = SecretStr(STRONG_PASSWORD)
    refresh_token = next(bearer_token_generator)
    redis_client.get = AsyncMock(return_value=refresh_token)
    user.is_email_verified = True
    uow.users.get_by_email = AsyncMock(return_value=user)

    await log_user(VALID_EMAIL, strong_password, redis_client, uow)
    redis_client.delete.assert_awaited_once_with(
        f"{KeyPrefix.REFRESH_TOKEN}:{refresh_token}", f"{KeyPrefix.USER_REFRESH_TOKEN}:{str(user.id)}"
    )
    uow.commit.assert_awaited_once()


async def test_log_user_no_existing_refresh_token(user, uow, key_value_repository, mock_hash_password):
    redis_client, pipeline = key_value_repository
    strong_password = SecretStr(STRONG_PASSWORD)
    redis_client.get = AsyncMock(return_value=None)
    await log_user(VALID_EMAIL, strong_password, redis_client, uow)
    pipeline.delete.assert_not_called()
    uow.commit.assert_awaited_once()


async def test_logout_user_success(key_value_repository, bearer_token_generator, uuid_generator):
    redis_client, pipeline = key_value_repository
    access_token = next(bearer_token_generator)
    refresh_token = next(bearer_token_generator)
    user_id = next(uuid_generator)
    redis_client.get = AsyncMock(return_value=refresh_token)

    result = await logout_user(access_token, user_id, redis_client)

    redis_client.get.assert_awaited_once_with(f"{KeyPrefix.USER_REFRESH_TOKEN}:{user_id}")
    redis_client.delete.assert_awaited_once_with(
        f"{KeyPrefix.REFRESH_TOKEN}:{refresh_token}",
        f"{KeyPrefix.USER_REFRESH_TOKEN}:{user_id}",
        f"{KeyPrefix.ACCESS_TOKEN}:{access_token}",
    )
    assert result is None


async def test_logout_user_no_refresh_token(key_value_repository, bearer_token_generator, uuid_generator):
    redis_client, pipeline = key_value_repository
    redis_client.get = AsyncMock(return_value=None)
    user_id = next(uuid_generator)
    access_token = next(bearer_token_generator)

    await logout_user(access_token, user_id, redis_client)

    redis_client.get.assert_awaited_once_with(f"{KeyPrefix.USER_REFRESH_TOKEN}:{user_id}")
    redis_client.delete.assert_awaited_once_with(
        f"{KeyPrefix.USER_REFRESH_TOKEN}:{user_id}", f"{KeyPrefix.ACCESS_TOKEN}:{access_token}"
    )


async def test_refresh_success(key_value_repository, bearer_token_generator, uuid_generator):
    redis_client, pipeline = key_value_repository
    user_id = next(uuid_generator)
    redis_client.get = AsyncMock(return_value=user_id)

    access_token = next(bearer_token_generator)
    refresh_token = next(bearer_token_generator)
    new_refresh_token = next(bearer_token_generator)

    with patch("app.domain.services.accounts.generate_token", side_effect=[access_token, new_refresh_token]):
        result = await refresh(refresh_token, redis_client)

    redis_client.get.assert_awaited_once_with(f"{KeyPrefix.REFRESH_TOKEN}:{refresh_token}")
    pipeline.delete.assert_awaited_once_with(f"{KeyPrefix.REFRESH_TOKEN}:{refresh_token}")
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
    redis_client, _ = key_value_repository
    not_existing_token = next(bearer_token_generator)
    redis_client.get = AsyncMock(return_value=None)

    with pytest.raises(InvalidCredentials):
        await refresh(not_existing_token, redis_client)
    redis_client.get.assert_awaited_once_with(f"{KeyPrefix.REFRESH_TOKEN}:{not_existing_token}")


async def test_refresh_user_not_found(key_value_repository, bearer_token_generator):
    redis_client, _ = key_value_repository
    expired_token = next(bearer_token_generator)
    redis_client.get = AsyncMock(return_value=None)

    with pytest.raises(InvalidCredentials):
        await refresh(expired_token, redis_client)
    redis_client.get.assert_awaited_once_with(f"{KeyPrefix.REFRESH_TOKEN}:{expired_token}")


async def test_verify_account_email_success(key_value_repository, uow, email_token_generator, uuid_generator):
    redis_client, _ = key_value_repository
    token = next(email_token_generator)
    user_id = next(uuid_generator)

    redis_client.get = AsyncMock(return_value=user_id)
    uow.users.verify_email = AsyncMock()
    redis_client.delete = AsyncMock()

    await verify_account_email(token, redis_client, uow)

    redis_client.get.assert_awaited_once_with(f"{KeyPrefix.EMAIL_VERIFICATION_TOKEN}:{token}")
    uow.users.verify_email.assert_awaited_once_with(user_id)
    redis_client.delete.assert_awaited_once_with(f"{KeyPrefix.EMAIL_VERIFICATION_TOKEN}:{token}")
    uow.commit.assert_awaited_once()


async def test_verify_account_email_invalid_token(key_value_repository, uow, email_token_generator):
    redis_client, _ = key_value_repository
    invalid_verification_token = next(email_token_generator)

    redis_client.get = AsyncMock(return_value=None)
    uow.users.verify_email = AsyncMock()
    redis_client.delete = AsyncMock()

    with pytest.raises(InvalidCredentials, match="Invalid verification token!"):
        await verify_account_email(invalid_verification_token, redis_client, uow)

    redis_client.get.assert_awaited_once_with(f"{KeyPrefix.EMAIL_VERIFICATION_TOKEN}:{invalid_verification_token}")
    uow.users.verify_email.assert_not_awaited()
    redis_client.delete.assert_not_awaited()
    uow.commit.assert_not_awaited()

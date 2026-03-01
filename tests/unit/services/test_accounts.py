from unittest.mock import AsyncMock

import pytest
from pydantic import SecretStr

from app.application.dtos.account import LoginData
from app.application.services.accounts import check_user_can_log
from app.domain.entities.user import User
from app.domain.services.security import hash_password
from tests.consts import STRONG_PASSWORD, VALID_USERNAME


@pytest.mark.asyncio
async def test_check_user_can_log_user_not_found(mock_users_repo):
    users_repo = mock_users_repo
    users_repo.get_by_username = AsyncMock(return_value=None)

    login_data = LoginData(username="unknown_user", password=SecretStr(STRONG_PASSWORD))

    result = await check_user_can_log(users_repo, login_data)

    assert result is None
    users_repo.get_by_username.assert_awaited_once_with("unknown_user")


@pytest.mark.asyncio
async def test_check_user_can_log_invalid_password(uuid_generator, mock_users_repo):
    user_id = next(uuid_generator)
    correct_password = SecretStr(STRONG_PASSWORD)
    hashed_password = hash_password(correct_password)
    user = User(id=user_id, username=VALID_USERNAME, hashed_password=hashed_password)

    users_repo = mock_users_repo
    users_repo.get_by_username = AsyncMock(return_value=user)

    login_data = LoginData(username=VALID_USERNAME, password=SecretStr("Wrong123!"))

    result = await check_user_can_log(users_repo, login_data)

    assert result is None
    users_repo.get_by_username.assert_awaited_once_with(VALID_USERNAME)


@pytest.mark.asyncio
async def test_check_user_can_log_success(uuid_generator, mock_users_repo):
    user_id = next(uuid_generator)
    password = SecretStr(STRONG_PASSWORD)
    hashed_password = hash_password(password)
    user = User(id=user_id, username=VALID_USERNAME, hashed_password=hashed_password)

    users_repo = mock_users_repo
    users_repo.get_by_username = AsyncMock(return_value=user)

    login_data = LoginData(username=VALID_USERNAME, password=password)

    result = await check_user_can_log(users_repo, login_data)

    assert result == user_id
    users_repo.get_by_username.assert_awaited_once_with(VALID_USERNAME)

from unittest.mock import patch

import pytest
from pydantic import SecretStr

from app.application.dtos.user import CreateUserData
from app.application.use_cases.account import CreateAccount, LoginData, ObjectExists
from app.domain.exceptions.users import UserExists
from tests.consts import STRONG_PASSWORD, VALID_USERNAME


@pytest.mark.asyncio
async def test_create_account_success(mock_session_maker, mock_opened_session, mock_users_repo):
    login_data = LoginData(username=VALID_USERNAME, password=SecretStr(STRONG_PASSWORD))

    with patch("app.application.use_cases.account.hash_password") as mock_hash:
        hash_value = b"hashed_secret"
        mock_hash.return_value = hash_value

        use_case = CreateAccount(session_maker=mock_session_maker, users_repo=mock_users_repo)

        await use_case.execute(login_data)

        mock_session_maker.begin.assert_called_once()

        create_data = CreateUserData(username=login_data.username, hashed_password=hash_value)
        mock_users_repo.add.assert_awaited_once_with(mock_opened_session, create_data)


@pytest.mark.asyncio
async def test_create_account_user_exists(mock_session_maker, mock_opened_session, mock_users_repo):
    login_data = LoginData(username="existinguser", password=SecretStr(STRONG_PASSWORD))

    mock_users_repo.add.side_effect = ObjectExists("User exists")

    with patch("app.application.use_cases.account.hash_password") as mock_hash:
        hash_value = b"hashed_secret"
        mock_hash.return_value = hash_value

        use_case = CreateAccount(session_maker=mock_session_maker, users_repo=mock_users_repo)

        with pytest.raises(UserExists):
            await use_case.execute(login_data)

        mock_users_repo.add.assert_awaited_once()

        create_data = CreateUserData(username=login_data.username, hashed_password=hash_value)
        mock_users_repo.add.assert_awaited_once_with(mock_opened_session, create_data)

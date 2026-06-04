from unittest.mock import patch

import pytest
from pydantic import SecretStr

from app.application.use_cases.account import CreateAccount, LoginData, ObjectExists
from app.domain.exceptions import UserExists
from tests.consts import STRONG_PASSWORD


# @pytest.mark.asyncio
# async def test_create_account_success(mock_session, mock_users_repo):
#     login_data = LoginData(username=VALID_USERNAME, password=SecretStr(STRONG_PASSWORD))
#
#     with patch("app.application.use_cases.account.hash_password") as mock_hash:
#         mock_hash.return_value = b"hashed_secret"
#
#         use_case = CreateAccount(session=mock_session, users_repo=mock_users_repo, login_data=login_data)
#
#         await use_case.execute()
#
#         mock_hash.assert_called_once_with(login_data.password)
#
#         expected_create_data = CreateUserData(username=VALID_USERNAME, hashed_password=b"hashed_secret")
#         mock_users_repo.add.assert_called_once_with(expected_create_data)
#
#         mock_session.commit.assert_called_once()
#
#
@pytest.mark.asyncio
async def test_create_account_user_exists(mock_session_maker, mock_users_repo):
    login_data = LoginData(username="existinguser", password=SecretStr(STRONG_PASSWORD))

    mock_users_repo.add.side_effect = ObjectExists("User exists")

    with patch("app.application.use_cases.account.hash_password") as mock_hash:
        mock_hash.return_value = b"hashed_secret"

        use_case = CreateAccount(session_maker=mock_session_maker, users_repo=mock_users_repo)

        with pytest.raises(UserExists):
            await use_case.execute(login_data)

        mock_users_repo.add.assert_called_once()
        mock_session_maker.begin.assert_called_once()

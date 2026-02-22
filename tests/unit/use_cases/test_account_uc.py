from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import SecretStr

from app.application.dtos.account import LoginData
from app.application.use_cases.account import CreateAccount
from app.domain.exceptions import UserExists
from app.domain.value_objects.user import CreateUserData
from app.shared.exceptions import ObjectExists


@pytest.fixture
def mock_session():
    session = MagicMock()
    # Mocking async context manager
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    session.commit = AsyncMock()
    return session


@pytest.fixture
def mock_users_repo():
    repo = MagicMock()
    repo.add = AsyncMock()
    return repo


@pytest.mark.asyncio
async def test_create_account_success(mock_session, mock_users_repo):
    login_data = LoginData(username="testuser", password=SecretStr("Password123!"))

    with patch("app.application.use_cases.account.hash_password") as mock_hash:
        mock_hash.return_value = b"hashed_secret"

        use_case = CreateAccount(session=mock_session, users_repo=mock_users_repo, login_data=login_data)

        await use_case.execute()

        # Verify password hashing
        mock_hash.assert_called_once_with(login_data.password)

        # Verify repo interaction
        expected_create_data = CreateUserData(username="testuser", hashed_password=b"hashed_secret")
        mock_users_repo.add.assert_called_once_with(expected_create_data)

        # Verify session commit
        mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_create_account_user_exists(mock_session, mock_users_repo):
    login_data = LoginData(username="existinguser", password=SecretStr("Password123!"))

    # Setup repo to raise ObjectExists
    mock_users_repo.add.side_effect = ObjectExists("User exists")

    with patch("app.application.use_cases.account.hash_password") as mock_hash:
        mock_hash.return_value = b"hashed_secret"

        use_case = CreateAccount(session=mock_session, users_repo=mock_users_repo, login_data=login_data)

        # Verify UserExists is raised
        with pytest.raises(UserExists):
            await use_case.execute()

        # Verify repo was called
        mock_users_repo.add.assert_called_once()

        # Verify commit was NOT called
        mock_session.commit.assert_not_called()

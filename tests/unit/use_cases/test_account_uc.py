from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.application.dtos.account import LoginData
from app.application.use_cases.account import CreateAccount, VerifyAccount
from app.shared.exceptions import InvalidCredentials, RelationalDbIntegrityError, UserExists


@pytest.fixture
def uow_mock():
    uow = MagicMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)

    uow.users = MagicMock()
    uow.users.add = AsyncMock()
    uow.users.verify_email = AsyncMock()
    return uow


@pytest.fixture
def token_verifier_mock():
    verifier = MagicMock()
    verifier.get_user_id_by_token = AsyncMock()
    verifier.invalidate_token = AsyncMock()
    return verifier


async def test_create_account_success(uow_mock):
    password = "StrongPass123!"
    data = LoginData(email="test@example.com", password=password)

    with patch("app.application.use_cases.account.hash_password", return_value="hashed") as hp:
        use_case = CreateAccount(users_unit_of_work=uow_mock, account_data=data)
        await use_case.execute()

    hp.assert_called_once_with(data.password)
    uow_mock.users.add.assert_awaited_once_with({"email": data.email, "hashed_password": "hashed"})


async def test_create_account_conflict_raises_user_exists(uow_mock):
    password = "StrongPass123!"
    data = LoginData(email="test@example.com", password=password)
    uow_mock.users.add.side_effect = RelationalDbIntegrityError()

    with patch("app.application.use_cases.account.hash_password", return_value="hashed"):
        use_case = CreateAccount(users_unit_of_work=uow_mock, account_data=data)

        with pytest.raises(UserExists):
            await use_case.execute()

    uow_mock.users.add.assert_awaited_once()


async def test_verify_account_success(uow_mock, token_verifier_mock):
    token_verifier_mock.get_user_id_by_token.return_value = 123

    use_case = VerifyAccount(email_token_verifier=token_verifier_mock, users_unit_of_work=uow_mock)
    await use_case.execute()

    token_verifier_mock.get_user_id_by_token.assert_awaited_once()
    uow_mock.users.verify_email.assert_awaited_once_with(123)
    token_verifier_mock.invalidate_token.assert_awaited_once()


async def test_verify_account_invalid_token_raises_invalid_credentials(uow_mock, token_verifier_mock):
    token_verifier_mock.get_user_id_by_token.return_value = None

    use_case = VerifyAccount(email_token_verifier=token_verifier_mock, users_unit_of_work=uow_mock)

    with pytest.raises(InvalidCredentials) as exc:
        await use_case.execute()

    assert "Invalid email verification token!" in str(exc.value)

    uow_mock.users.verify_email.assert_not_awaited()
    token_verifier_mock.invalidate_token.assert_not_awaited()

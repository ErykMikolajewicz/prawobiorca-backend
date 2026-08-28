from pydantic import SecretStr

from app.application.dtos.account import LoginData
from app.application.services.accounts import check_user_can_log
from app.domain.entities.user import User
from app.domain.services.security import hash_password
from tests.consts import STRONG_PASSWORD, VALID_USERNAME


async def test_check_user_can_log_user_not_found(mock_session, mock_users_repo):
    mock_users_repo.get_by_username.return_value = None

    login_data = LoginData(username="unknown_user", password=SecretStr(STRONG_PASSWORD))

    result = await check_user_can_log(mock_session, mock_users_repo, login_data)

    assert result is None
    mock_users_repo.get_by_username.assert_awaited_once_with(mock_session, "unknown_user")


async def test_check_user_can_log_invalid_password(mock_session, mock_users_repo, uuid_generator):
    user_id = next(uuid_generator)
    correct_password = SecretStr(STRONG_PASSWORD)
    hashed_password = hash_password(correct_password)
    user = User(id=user_id, username=VALID_USERNAME, hashed_password=hashed_password)

    users_repo = mock_users_repo
    users_repo.get_by_username.return_value = user

    login_data = LoginData(username=VALID_USERNAME, password=SecretStr("Wrong123!"))

    result = await check_user_can_log(mock_session, users_repo, login_data)

    assert result is None
    users_repo.get_by_username.assert_awaited_once_with(mock_session, VALID_USERNAME)


async def test_check_user_can_log_success(mock_session, mock_users_repo, uuid_generator):
    user_id = next(uuid_generator)
    password = SecretStr(STRONG_PASSWORD)
    hashed_password = hash_password(password)
    user = User(id=user_id, username=VALID_USERNAME, hashed_password=hashed_password)

    users_repo = mock_users_repo
    users_repo.get_by_username.return_value = user

    login_data = LoginData(username=VALID_USERNAME, password=password)

    result = await check_user_can_log(mock_session, users_repo, login_data)

    assert result == user_id
    users_repo.get_by_username.assert_awaited_once_with(mock_session, VALID_USERNAME)

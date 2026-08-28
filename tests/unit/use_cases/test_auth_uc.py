from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from pydantic import SecretStr

from app.application.dtos.account import LoginData
from app.application.dtos.auth import LoginOutput
from app.application.use_cases.auth import LogoutUser, LogUser
from app.domain.exceptions.users import UserCantLog
from tests.consts import AUTHORIZATION_TOKEN, VALID_USERNAME


async def test_log_user_success(
    mock_opened_session,
    mock_session_maker,
    mock_users_repo,
    mock_tokens_repo,
    uuid_generator,
):
    login_data = LoginData(username=VALID_USERNAME, password=SecretStr("Password123!"))
    user_id = next(uuid_generator)

    with (
        patch("app.application.use_cases.auth.check_user_can_log", new_callable=AsyncMock) as mock_check,
        patch("app.application.use_cases.auth.generate_authorization_token") as mock_gen_token,
        patch("app.application.use_cases.auth.prevent_timing_attack", new_callable=AsyncMock) as mock_prevent,
    ):
        mock_check.return_value = user_id
        mock_gen_token.return_value = AUTHORIZATION_TOKEN

        use_case = LogUser(session_maker=mock_session_maker, users_repo=mock_users_repo, tokens_repo=mock_tokens_repo)

        result = await use_case.execute(login_data)

        mock_check.assert_called_once_with(mock_opened_session, mock_users_repo, login_data)
        mock_prevent.assert_not_called()
        mock_gen_token.assert_called_once()

        mock_tokens_repo.add_token.assert_called_once()
        call_args = mock_tokens_repo.add_token.call_args
        assert call_args[0][1] == user_id
        assert call_args[0][2] == AUTHORIZATION_TOKEN
        assert isinstance(call_args[0][3], datetime)

        assert call_args[0][3].tzinfo == timezone.utc

        assert isinstance(result, LoginOutput)
        assert result.session_id == AUTHORIZATION_TOKEN

        assert result.expires_in > 0


async def test_log_user_failure(
    mock_opened_session,
    mock_session_maker,
    mock_users_repo,
    mock_tokens_repo,
):
    login_data = LoginData(username=VALID_USERNAME, password=SecretStr("WrongPassword123!"))

    with (
        patch("app.application.use_cases.auth.check_user_can_log", new_callable=AsyncMock) as mock_check,
        patch("app.application.use_cases.auth.generate_authorization_token") as mock_gen_token,
        patch("app.application.use_cases.auth.prevent_timing_attack", new_callable=AsyncMock) as mock_prevent,
        patch("app.application.use_cases.auth.asyncio.get_event_loop") as mock_loop,
    ):
        mock_check.return_value = None
        fake_time = 12345.6
        mock_loop.return_value.time.return_value = fake_time

        use_case = LogUser(session_maker=mock_session_maker, users_repo=mock_users_repo, tokens_repo=mock_tokens_repo)

        with pytest.raises(UserCantLog):
            await use_case.execute(login_data)

        mock_check.assert_called_once_with(mock_opened_session, mock_users_repo, login_data)
        mock_prevent.assert_called_once_with(fake_time)
        mock_gen_token.assert_not_called()
        mock_tokens_repo.add_token.assert_not_called()


async def test_logout_user(mock_opened_session, mock_session_maker, mock_tokens_repo):

    use_case = LogoutUser(session_maker=mock_session_maker, tokens_repo=mock_tokens_repo)

    await use_case.execute(authorization_token=AUTHORIZATION_TOKEN)

    mock_tokens_repo.invalidate_token.assert_called_once_with(mock_opened_session, AUTHORIZATION_TOKEN)

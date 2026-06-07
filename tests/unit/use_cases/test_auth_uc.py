from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from pydantic import SecretStr

from app.application.dtos.account import LoginData
from app.application.dtos.auth import LoginOutput
from app.application.use_cases.auth import LogoutUser, LogUser
from tests.consts import VALID_USERNAME


@pytest.mark.asyncio
async def test_log_user_success(
    mock_opened_session, mock_session_maker, mock_users_repo, mock_tokens_repo, session_id_generator, uuid_generator
):
    login_data = LoginData(username=VALID_USERNAME, password=SecretStr("Password123!"))
    expected_session_id = next(session_id_generator)
    user_id = next(uuid_generator)

    with (
        patch("app.application.use_cases.auth.check_user_can_log", new_callable=AsyncMock) as mock_check,
        patch("app.application.use_cases.auth.generate_session_id") as mock_gen_session,
        patch("app.application.use_cases.auth.prevent_timing_attack", new_callable=AsyncMock) as mock_prevent,
    ):
        mock_check.return_value = user_id
        mock_gen_session.return_value = expected_session_id

        use_case = LogUser(session_maker=mock_session_maker, users_repo=mock_users_repo, tokens_repo=mock_tokens_repo)

        result = await use_case.execute(login_data)

        mock_check.assert_called_once_with(mock_opened_session, mock_users_repo, login_data)
        mock_prevent.assert_not_called()
        mock_gen_session.assert_called_once()

        mock_tokens_repo.add_session.assert_called_once()
        call_args = mock_tokens_repo.add_session.call_args
        assert call_args[0][1] == user_id
        assert call_args[0][2] == expected_session_id
        assert isinstance(call_args[0][3], datetime)

        assert call_args[0][3].tzinfo == timezone.utc

        assert isinstance(result, LoginOutput)
        assert result.session_id == expected_session_id

        assert result.expires_in > 0


@pytest.mark.asyncio
async def test_logout_user(mock_opened_session, mock_session_maker, mock_tokens_repo, session_id_generator):
    session_id = next(session_id_generator)

    use_case = LogoutUser(session_maker=mock_session_maker, tokens_repo=mock_tokens_repo)

    await use_case.execute(session_id=session_id)

    mock_tokens_repo.invalidate_session.assert_called_once_with(mock_opened_session, session_id)

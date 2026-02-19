from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.application.dtos.account import LoginData
from app.application.use_cases.auth import SESSION_DURATION_SECONDS, LogoutUser, LogUser
from app.domain.exceptions import UserCantLog
from app.shared.enums import TokenType


@pytest.fixture
def key_value_repo():
    return MagicMock()


@pytest.fixture
def pipeline():
    p = AsyncMock()
    p.execute = AsyncMock()
    return p


@pytest.fixture
def pipeline_context_manager(pipeline):
    cm = AsyncMock()
    cm.__aenter__.return_value = pipeline
    cm.__aexit__.return_value = False
    return cm


@pytest.fixture
def key_value_repo_with_pipeline(pipeline_context_manager):
    repo = MagicMock()
    repo.pipeline.return_value = pipeline_context_manager
    return repo


@pytest.fixture
def access_tokens_reader():
    return AsyncMock()


@pytest.fixture
def users_uow():
    uow = AsyncMock()
    uow.__aenter__.return_value = uow
    uow.__aexit__.return_value = False
    uow.users_tokens = AsyncMock()
    return uow


@pytest.fixture
def login_data():
    return LoginData(username="example@example.com", password="StrongPassword3!")


@pytest.fixture
def tokens_payload():
    return {
        "access_token": "access_token_value",
        "expires_in": SESSION_DURATION_SECONDS,
        "token_type": TokenType.BEARER,
    }


async def test_log_user_success(users_uow, login_data, tokens_payload, uuid_generator):
    user_id = next(uuid_generator)
    fixed_token = tokens_payload["access_token"]

    with (
        patch("app.application.use_cases.auth.check_user_can_log", new_callable=AsyncMock) as check_can_log,
        patch("app.application.use_cases.auth.generate_token", return_value=fixed_token) as generate,
    ):
        check_can_log.return_value = str(user_id)
        before = datetime.now(timezone.utc)

        uc = LogUser(users_unit_of_work=users_uow, login_data=login_data)
        result = await uc.execute()

        after = datetime.now(timezone.utc)

    assert result.access_token == tokens_payload["access_token"]
    assert result.expires_in == tokens_payload["expires_in"]
    assert result.token_type == tokens_payload["token_type"]

    check_can_log.assert_awaited_once_with(users_uow, login_data)
    generate.assert_called_once_with()
    users_uow.users_tokens.add_token.assert_awaited_once()

    add_args = users_uow.users_tokens.add_token.call_args.args
    assert add_args[0] == user_id
    assert add_args[1] == fixed_token
    valid_until = add_args[2]
    assert isinstance(valid_until, datetime)
    assert (
        before + timedelta(seconds=SESSION_DURATION_SECONDS)
        <= valid_until
        <= after + timedelta(seconds=SESSION_DURATION_SECONDS)
    )


async def test_log_user_user_cant_log_calls_prevent_timing_attack_and_raises(users_uow, login_data):
    with (
        patch("app.application.use_cases.auth.check_user_can_log", new_callable=AsyncMock) as check_can_log,
        patch("app.application.use_cases.auth.prevent_timing_attack", new_callable=AsyncMock) as prevent,
    ):
        check_can_log.return_value = None

        uc = LogUser(users_unit_of_work=users_uow, login_data=login_data)

        with pytest.raises(UserCantLog):
            await uc.execute()

    check_can_log.assert_awaited_once_with(users_uow, login_data)
    prevent.assert_awaited_once()


async def test_logout_user_success_with_refresh_token(
    key_value_repo_with_pipeline, pipeline, access_tokens_reader, uuid_generator
):
    access_token = "access_token"
    user_id = next(uuid_generator)
    refresh_token = "refresh_token"

    access_tokens_reader.get_refresh_token_by_user.return_value = refresh_token

    with patch("app.application.use_cases.auth.AccessTokensManager") as Manager:
        manager = AsyncMock()
        Manager.return_value = manager
        manager.invalidate_refresh_token = AsyncMock()
        manager.invalidate_refresh_token_user = AsyncMock()
        manager.invalidate_access_token = AsyncMock()

        use_case = LogoutUser(
            key_value_repo=key_value_repo_with_pipeline,
            access_tokens_reader=access_tokens_reader,
            access_token=access_token,
            user_id=user_id,
        )

        await use_case.execute()

    access_tokens_reader.get_refresh_token_by_user.assert_awaited_once_with(user_id)
    Manager.assert_called_once_with(pipeline)

    manager.invalidate_refresh_token.assert_awaited_once_with(refresh_token)
    manager.invalidate_refresh_token_user.assert_awaited_once_with(user_id)
    manager.invalidate_access_token.assert_awaited_once_with(access_token)
    pipeline.execute.assert_awaited_once()

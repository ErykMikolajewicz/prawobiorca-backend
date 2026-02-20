from unittest.mock import AsyncMock, MagicMock

import pytest


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

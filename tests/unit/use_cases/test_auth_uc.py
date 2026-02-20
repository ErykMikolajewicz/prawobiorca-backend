from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.dtos.account import LoginData
from app.application.use_cases.auth import SESSION_DURATION_SECONDS
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

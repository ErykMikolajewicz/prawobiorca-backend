from unittest.mock import AsyncMock

import pytest
from fastapi import Request

from app.framework.dependencies.authentication import set_user_by_session_id
from main import app


@pytest.fixture(scope="function")
def assure_use_case_not_executed():
    mock = AsyncMock()

    def __overrider(use_case_getter):
        app.dependency_overrides[use_case_getter] = lambda: mock

    yield __overrider
    try:
        mock.execute.assert_not_called()
    finally:
        app.dependency_overrides = {}


@pytest.fixture
def override_validate_token(bearer_token_generator, uuid_generator):
    access_token = next(bearer_token_generator)
    user_id = next(uuid_generator)

    def _override(request: Request):
        request.state.user_id = user_id
        return access_token, user_id

    app.dependency_overrides[set_user_by_session_id] = _override
    yield access_token, user_id
    app.dependency_overrides = {}

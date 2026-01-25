from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException, Request, status

from app.framework.dependencies.authentication import validate_token
from app.framework.dependencies.file_storage import get_file_storage
from app.infrastructure.relational_db.units_of_work.users import UsersUnitOfWork
from main import app


@pytest.fixture(scope='function')
def assure_use_case_not_executed():
    mock =  AsyncMock()

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

    app.dependency_overrides[validate_token] = _override
    yield access_token, user_id
    app.dependency_overrides = {}

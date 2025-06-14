from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException, Request, status
from fastapi.testclient import TestClient

from app.cloud_storage.connection import get_storage_client
from app.core.authentication import validate_token
from app.key_value_db.connection import get_redis
from app.main import app
from app.units_of_work.users import UsersUnitOfWork


@pytest.fixture
def client():
    return TestClient(app)


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


@pytest.fixture
def override_get_storage_client():
    def _override():
        return AsyncMock()

    app.dependency_overrides[get_storage_client] = _override
    yield
    app.dependency_overrides = {}


@pytest.fixture
def override_users_unit_of_work():
    def _override():
        return AsyncMock()

    app.dependency_overrides[UsersUnitOfWork] = _override
    yield
    app.dependency_overrides = {}


@pytest.fixture
def override_get_redis():
    def _override():
        return AsyncMock()

    app.dependency_overrides[get_redis] = _override
    yield
    app.dependency_overrides = {}


@pytest.fixture
def override_validate_token_unauthorized():
    def _override():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    app.dependency_overrides[validate_token] = _override
    yield
    app.dependency_overrides = {}

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient
from fastapi import status

from app.main import app
from app.core.exceptions import FileNameExist, EmptyFileException
from app.core.authentication import validate_token
from app.cloud_storage.connection import get_storage_client
from app.units_of_work.users import UsersUnitOfWork
from app.core.security import generate_token


valid_bearer_token = generate_token() # It is random, not valid in sense exist in database


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def override_validate_token():
    def _override():
        return valid_bearer_token, "user-123"
    app.dependency_overrides[validate_token] = _override
    yield
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
def mock_add_user_file():
    with patch("app.services.user_files.add_user_file", new_callable=AsyncMock) as mock:
        yield mock


def test_add_user_file_success(client, override_validate_token, override_get_storage_client,
                               override_users_unit_of_work, mock_add_user_file):
    file_content = b"test"
    file = ("test.txt", file_content, "text/plain")
    headers = {"Authorization": f"Bearer {valid_bearer_token}"}

    response = client.post(
        "/user/files",
        files={"user_file": file},
        headers=headers
    )

    assert response.status_code == status.HTTP_201_CREATED
    mock_add_user_file.assert_awaited_once()


def test_add_user_file_missing_file_field(client, override_validate_token, override_get_storage_client,
                                          override_users_unit_of_work, mock_add_user_file):
    headers = {"Authorization": f"Bearer {valid_bearer_token}"}

    response = client.post(
        "/user/files",
        headers=headers,
        files={}
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    mock_add_user_file.assert_not_awaited()


def test_add_user_file_name_exist(client, override_validate_token, override_get_storage_client,
                                  override_users_unit_of_work, mock_add_user_file):
    mock_add_user_file.side_effect = FileNameExist()
    file_content = b"duplicate"
    file = ("duplicate.txt", file_content, "text/plain")
    headers = {"Authorization": f"Bearer {valid_bearer_token}"}

    response = client.post(
        "/user/files",
        files={"user_file": file},
        headers=headers
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {"detail": "File with that name already exist!"}
    mock_add_user_file.assert_awaited_once()


def test_add_user_file_empty_file(client, override_validate_token, override_get_storage_client,
                                  override_users_unit_of_work, mock_add_user_file):
    mock_add_user_file.side_effect = EmptyFileException()
    empty_file = ("empty.txt", b"", "text/plain")
    headers = {"Authorization": f"Bearer {valid_bearer_token}"}

    response = client.post(
        "/user/files",
        files={"user_file": empty_file},
        headers=headers
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "File can not be empty!"}
    mock_add_user_file.assert_awaited_once()


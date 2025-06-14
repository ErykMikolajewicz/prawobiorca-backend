from unittest.mock import AsyncMock, patch

import pytest
from fastapi import status

from app.shared.exceptions import EmptyFileException, FileNameExist


@pytest.fixture
def mock_add_user_file():
    with patch("app.domain.services.user_files.add_user_file", new_callable=AsyncMock) as mock:
        yield mock


def test_add_user_file_success(
    client, override_validate_token, override_get_storage_client, override_users_unit_of_work, mock_add_user_file
):
    access_token, _ = override_validate_token
    file_content = b"test"
    file = ("test.txt", file_content, "text/plain")
    headers = {"Authorization": f"Bearer {access_token}"}

    response = client.post("/user/files", files={"user_file": file}, headers=headers)

    assert response.status_code == status.HTTP_201_CREATED
    mock_add_user_file.assert_awaited_once()


def test_add_user_file_missing_file_field(
    client, override_validate_token, override_get_storage_client, override_users_unit_of_work, mock_add_user_file
):
    access_token, _ = override_validate_token
    headers = {"Authorization": f"Bearer {access_token}"}

    response = client.post("/user/files", headers=headers, files={})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    mock_add_user_file.assert_not_awaited()


def test_add_user_file_name_exist(
    client, override_validate_token, override_get_storage_client, override_users_unit_of_work, mock_add_user_file
):
    access_token, _ = override_validate_token
    mock_add_user_file.side_effect = FileNameExist()
    file_content = b"duplicate"
    file = ("duplicate.txt", file_content, "text/plain")
    headers = {"Authorization": f"Bearer {access_token}"}

    response = client.post("/user/files", files={"user_file": file}, headers=headers)

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {"detail": "File with that name already exist!"}
    mock_add_user_file.assert_awaited_once()


def test_add_user_file_empty_file(
    client, override_validate_token, override_get_storage_client, override_users_unit_of_work, mock_add_user_file
):
    access_token, _ = override_validate_token
    mock_add_user_file.side_effect = EmptyFileException()
    empty_file = ("empty.txt", b"", "text/plain")
    headers = {"Authorization": f"Bearer {access_token}"}

    response = client.post("/user/files", files={"user_file": empty_file}, headers=headers)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "File can not be empty!"}
    mock_add_user_file.assert_awaited_once()

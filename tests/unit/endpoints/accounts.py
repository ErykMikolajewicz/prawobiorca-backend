from unittest.mock import AsyncMock, patch
from unittest.mock import ANY

import pytest
from fastapi.testclient import TestClient
from fastapi import status

from app.main import app
from app.core.exceptions import UserExists, UserNotFound, InvalidCredentials
from app.core.consts import BEARER_TOKEN_LENGTH


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_users_unit_of_work():
    with patch("app.services.accounts.create_account", new_callable=AsyncMock) as mock_create_account:
        yield mock_create_account


def test_create_account_success(client, mock_users_unit_of_work):
    payload = {"login": "testuser", "password": "StrongPassword1!"}

    response = client.post("/accounts", json=payload)

    assert response.status_code == status.HTTP_201_CREATED
    mock_users_unit_of_work.assert_awaited_once()


def test_create_account_conflict(client, mock_users_unit_of_work):
    mock_users_unit_of_work.side_effect = UserExists()
    payload = {"login": "existinguser", "password": "StrongPassword1!"}

    response = client.post("/accounts", json=payload)

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {"detail": "User with that login already exist!"}
    mock_users_unit_of_work.assert_awaited_once()


@pytest.mark.parametrize(
    "password, error_detail",
    [
        ("nouppercase1!", "Password must contain at least one uppercase letter."),
        ("NOLOWERCASE1!", "Password must contain at least one lowercase letter."),
        ("NoDigits!!", "Password must contain at least one digit."),
        ("NoSpecial1", "Password must contain at least one special character."),
    ]
)
def test_create_account_weak_passwords(client, password, error_detail):
    payload = {"login": "validlogin", "password": password}

    response = client.post("/accounts", json=payload)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert error_detail in response.text


@pytest.mark.parametrize(
    "login",
    ["in valid", "with@symbol", "!", "", "a"]
)
def test_create_account_invalid_login(client, login):
    payload = {"login": login, "password": "ValidPass1!"}

    response = client.post("/accounts", json=payload)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.fixture
def mock_log_user():
    with patch("app.services.accounts.log_user", new_callable=AsyncMock) as mock:
        yield mock


def test_login_success(client, mock_log_user):
    mock_log_user.return_value = {
        "access_token": "a" * BEARER_TOKEN_LENGTH,
        "expires_in": 3600,
        "token_type": "bearer"
    }

    data = {"username": "testuser", "password": "StrongPassword1!"}
    response = client.post("/auth/login", data=data)

    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    assert "access_token" in result
    assert "expires_in" in result
    assert "token_type" in result
    assert result["token_type"] == "bearer"
    assert len(result["access_token"]) == BEARER_TOKEN_LENGTH
    mock_log_user.assert_awaited_once_with("testuser", "StrongPassword1!", ANY)


def test_login_user_not_found(client, mock_log_user):
    mock_log_user.side_effect = UserNotFound()

    data = {"username": "nouser", "password": "anyPassword1!"}
    response = client.post("/auth/login", data=data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Invalid credentials!"}
    mock_log_user.assert_awaited_once_with("nouser", "anyPassword1!", ANY)


def test_login_invalid_password(client, mock_log_user):
    mock_log_user.side_effect = InvalidCredentials()

    data = {"username": "testuser", "password": "wrongPassword1!"}
    response = client.post("/auth/login", data=data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Invalid credentials!"}
    mock_log_user.assert_awaited_once_with("testuser", "wrongPassword1!", ANY)


@pytest.mark.parametrize(
    "data,expected_status",
    [
        ({}, status.HTTP_422_UNPROCESSABLE_ENTITY),
        ({"username": "user"}, status.HTTP_422_UNPROCESSABLE_ENTITY),
        ({"password": "Pass1!"}, status.HTTP_422_UNPROCESSABLE_ENTITY),
        ({"username": "", "password": "Pass1!"}, status.HTTP_401_UNAUTHORIZED),
        ({"username": "user", "password": ""}, status.HTTP_401_UNAUTHORIZED),
    ]
)
def test_login_missing_fields(client, mock_log_user, data, expected_status):
    if data.get("username", "") == "" or data.get("password", "") == "":
        mock_log_user.side_effect = UserNotFound()
    response = client.post("/auth/login", data=data)
    assert response.status_code == expected_status

from unittest.mock import AsyncMock, patch
from unittest.mock import ANY

import pytest
from fastapi import status

from app.core.exceptions import UserExists, UserNotFound, InvalidCredentials
from app.core.security import url_safe_bearer_token_length
from tests.unit.consts import valid_bearer_token, invalid_bearer_token


@pytest.fixture
def mock_users_unit_of_work():
    with patch("app.services.accounts.create_account", new_callable=AsyncMock) as mock_create_account:
        yield mock_create_account


@pytest.fixture
def mock_refresh_token():
    with patch("app.services.accounts.refresh", new_callable=AsyncMock) as mock:
        yield mock


@pytest.fixture
def mock_log_user():
    with patch("app.services.accounts.log_user", new_callable=AsyncMock) as mock:
        yield mock


@pytest.fixture
def mock_logout_user():
    with patch("app.services.accounts.logout_user", new_callable=AsyncMock) as mock:
        yield mock


def test_create_account_success(client, mock_users_unit_of_work):
    payload = {"login": "test_user", "password": "StrongPassword1!"}

    response = client.post("/accounts", json=payload)

    assert response.status_code == status.HTTP_201_CREATED
    mock_users_unit_of_work.assert_awaited_once()


def test_create_account_conflict(client, mock_users_unit_of_work):
    mock_users_unit_of_work.side_effect = UserExists()
    payload = {"login": "existing_user", "password": "StrongPassword1!"}

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
    payload = {"login": "valid_login", "password": password}

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


def test_login_success(client, mock_log_user):
    mock_log_user.return_value = {
        "access_token": "a" * url_safe_bearer_token_length,
        "expires_in": 3600,
        "token_type": "bearer",
        "refresh_token": "a" * url_safe_bearer_token_length
    }

    data = {"username": "test_user", "password": "StrongPassword1!"}
    response = client.post("/auth/login", data=data)

    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    assert "access_token" in result
    assert "expires_in" in result
    assert "token_type" in result
    assert result["token_type"] == "bearer"
    assert len(result["access_token"]) == url_safe_bearer_token_length
    mock_log_user.assert_awaited_once_with("test_user", "StrongPassword1!", ANY, ANY)


def test_login_user_not_found(client, mock_log_user):
    mock_log_user.side_effect = UserNotFound()

    data = {"username": "no_user", "password": "anyPassword1!"}
    response = client.post("/auth/login", data=data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Invalid credentials!"}
    mock_log_user.assert_awaited_once_with("no_user", "anyPassword1!", ANY, ANY)


def test_login_invalid_password(client, mock_log_user):
    mock_log_user.side_effect = InvalidCredentials()

    data = {"username": "test_user", "password": "wrongPassword1!"}
    response = client.post("/auth/login", data=data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Invalid credentials!"}
    mock_log_user.assert_awaited_once_with("test_user", "wrongPassword1!", ANY, ANY)


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


def test_logout_success(client, override_validate_token, mock_logout_user):
    headers = {"Authorization": f"Bearer {valid_bearer_token}"}
    response = client.post("/auth/logout", headers=headers)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    mock_logout_user.assert_awaited_once_with(valid_bearer_token, "user-123", ANY)


def test_logout_invalid_token(client, mock_logout_user, override_validate_token_unauthorized, override_get_redis):
    headers = {"Authorization": f"Bearer {invalid_bearer_token}"}
    response = client.post("/auth/logout", headers=headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    mock_logout_user.assert_not_called()


def test_logout_missing_authorization_header(client, mock_logout_user):
    response = client.post("/auth/logout")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    mock_logout_user.assert_not_called()


def test_refresh_success(client, mock_refresh_token):
    mock_refresh_token.return_value = {
        "access_token": valid_bearer_token,
        "expires_in": 3600,
        "token_type": "bearer",
        "refresh_token": valid_bearer_token
    }
    headers = {"X-Refresh-Token": valid_bearer_token}

    response = client.post("/auth/refresh", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    assert set(result.keys()) == {"access_token", "expires_in", "token_type", "refresh_token"}
    assert result["token_type"] == "bearer"
    assert len(result["access_token"]) == url_safe_bearer_token_length
    assert len(result["refresh_token"]) == url_safe_bearer_token_length
    mock_refresh_token.assert_awaited_once_with(valid_bearer_token, ANY)


def test_refresh_missing_header(client, mock_refresh_token):
    response = client.post("/auth/refresh")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    mock_refresh_token.assert_not_called()


def test_refresh_empty_token(client, mock_refresh_token):
    headers = {"X-Refresh-Token": ""}
    response = client.post("/auth/refresh", headers=headers)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    mock_refresh_token.assert_not_called()


def test_refresh_invalid_token(client, mock_refresh_token):
    mock_refresh_token.side_effect = InvalidCredentials()
    headers = {"X-Refresh-Token": invalid_bearer_token}

    response = client.post("/auth/refresh", headers=headers)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Invalid refresh token!"}
    mock_refresh_token.assert_awaited_once_with(invalid_bearer_token, ANY)

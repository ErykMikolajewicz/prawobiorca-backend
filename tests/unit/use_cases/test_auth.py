from unittest.mock import ANY, AsyncMock, patch

import pytest
from fastapi import status
from pydantic import SecretStr

from app.domain.services.security import url_safe_bearer_token_length
from app.shared.enums import TokenType
from app.shared.exceptions import InvalidCredentials, UserNotFound
from tests.consts import STRONG_PASSWORD
from app.shared.settings.application import app_settings

ACCESS_TOKEN_EXPIRATION_SECONDS = app_settings.ACCESS_TOKEN_EXPIRATION_SECONDS
REFRESH_TOKEN_EXPIRATION_SECONDS = app_settings.REFRESH_TOKEN_EXPIRATION_SECONDS


@pytest.fixture
def mock_refresh_token():
    with patch("app.domain.services.accounts.refresh", new_callable=AsyncMock) as mock:
        yield mock


@pytest.fixture
def mock_log_user():
    with patch("app.domain.services.accounts.log_user", new_callable=AsyncMock) as mock:
        yield mock


@pytest.fixture
def mock_logout_user():
    with patch("app.domain.services.accounts.logout_user", new_callable=AsyncMock) as mock:
        yield mock


def test_login_success(client, mock_log_user, bearer_token_generator):
    access_token = next(bearer_token_generator)
    refresh_token = next(bearer_token_generator)
    mock_log_user.return_value = {
        "access_token": access_token,
        "expires_in": REFRESH_TOKEN_EXPIRATION_SECONDS,
        "token_type": TokenType.BEARER,
        "refresh_token": refresh_token,
    }

    data = {"username": "test_user", "password": STRONG_PASSWORD}
    response = client.post("/auth/login", data=data)

    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    assert "access_token" in result
    assert "expires_in" in result
    assert "token_type" in result
    assert result["token_type"] == TokenType.BEARER
    assert len(result["access_token"]) == url_safe_bearer_token_length
    mock_log_user.assert_awaited_once_with("test_user", SecretStr(STRONG_PASSWORD), ANY, ANY)


def test_login_user_not_found(client, mock_log_user):
    mock_log_user.side_effect = UserNotFound()

    data = {"username": "no_user", "password": STRONG_PASSWORD}
    with patch("asyncio.sleep", new=AsyncMock()) as mock_sleep:
        response = client.post("/auth/login", data=data)
        mock_sleep.assert_called()

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Invalid credentials!"}
    mock_log_user.assert_awaited_once_with("no_user", SecretStr(STRONG_PASSWORD), ANY, ANY)


def test_login_invalid_password(client, mock_log_user):
    mock_log_user.side_effect = InvalidCredentials()
    wrong_password = STRONG_PASSWORD

    data = {"username": "test_user", "password": wrong_password}
    with patch("asyncio.sleep", new=AsyncMock()) as mock_sleep:
        response = client.post("/auth/login", data=data)
        mock_sleep.assert_called()

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Invalid credentials!"}
    mock_log_user.assert_awaited_once_with("test_user", SecretStr(wrong_password), ANY, ANY)


def test_logout_success(client, override_validate_token, mock_logout_user, bearer_token_generator):
    access_token, user_id = override_validate_token
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.post("/auth/logout", headers=headers)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    mock_logout_user.assert_awaited_once_with(access_token, user_id, ANY)


def test_logout_invalid_token(client, mock_logout_user, override_validate_token_unauthorized, bearer_token_generator):
    invalid_access_token = next(bearer_token_generator)
    headers = {"Authorization": f"Bearer {invalid_access_token}"}
    response = client.post("/auth/logout", headers=headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    mock_logout_user.assert_not_called()


def test_logout_missing_authorization_header(client, mock_logout_user):
    response = client.post("/auth/logout")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    mock_logout_user.assert_not_called()


def test_refresh_success(client, mock_refresh_token, bearer_token_generator):
    refresh_token = next(bearer_token_generator)
    headers = {"X-Refresh-Token": refresh_token}

    new_access_token = next(bearer_token_generator)
    new_refresh_token = next(bearer_token_generator)
    mock_refresh_token.return_value = {
        "access_token": new_access_token,
        "expires_in": REFRESH_TOKEN_EXPIRATION_SECONDS,
        "token_type": TokenType.BEARER,
        "refresh_token": new_refresh_token,
    }

    response = client.post("/auth/refresh", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    assert set(result.keys()) == {"access_token", "expires_in", "token_type", "refresh_token"}
    assert result["token_type"] == TokenType.BEARER
    assert len(result["access_token"]) == url_safe_bearer_token_length
    assert len(result["refresh_token"]) == url_safe_bearer_token_length
    mock_refresh_token.assert_awaited_once_with(refresh_token, ANY)


def test_refresh_invalid_token(client, mock_refresh_token, bearer_token_generator):
    invalid_refresh_token = next(bearer_token_generator)
    mock_refresh_token.side_effect = InvalidCredentials()
    headers = {"X-Refresh-Token": invalid_refresh_token}

    response = client.post("/auth/refresh", headers=headers)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Invalid refresh token!"}
    mock_refresh_token.assert_awaited_once_with(invalid_refresh_token, ANY)
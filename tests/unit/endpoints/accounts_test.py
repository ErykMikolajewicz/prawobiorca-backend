from unittest.mock import ANY, AsyncMock, patch

import pytest
from fastapi import status
from pydantic import SecretStr

from app.config import settings
from app.infrastructure.utilities.security import url_safe_bearer_token_length
from app.shared.enums import TokenType
from app.shared.exceptions import InvalidCredentials, UserExists, UserNotFound
from tests.test_consts import STRONG_PASSWORD, VALID_EMAIL

REFRESH_TOKEN_EXPIRATION_SECONDS = settings.app.REFRESH_TOKEN_EXPIRATION_SECONDS


@pytest.fixture
def mock_create_account():
    with patch("app.domain.services.accounts.create_account", new_callable=AsyncMock) as mock_create_account:
        yield mock_create_account


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


@pytest.fixture
def mock_verify_account_email():
    with patch("app.domain.services.accounts.verify_account_email", new_callable=AsyncMock) as mock:
        yield mock


def test_create_account_success(client, mock_create_account):
    payload = {"email": VALID_EMAIL, "password": STRONG_PASSWORD}

    response = client.post("/accounts", json=payload)

    assert response.status_code == status.HTTP_201_CREATED
    mock_create_account.assert_awaited_once()


def test_create_account_conflict(client, mock_create_account):
    mock_create_account.side_effect = UserExists()
    existing_email = VALID_EMAIL
    payload = {"email": existing_email, "password": STRONG_PASSWORD}

    response = client.post("/accounts", json=payload)

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {"detail": "User with that email already exist!"}
    mock_create_account.assert_awaited_once()


@pytest.mark.parametrize(
    "password, error_detail",
    [
        ("nouppercase1!", "Password must contain at least one uppercase letter."),
        ("NOLOWERCASE1!", "Password must contain at least one lowercase letter."),
        ("NoDigits!!", "Password must contain at least one digit."),
        ("NoSpecial1", "Password must contain at least one special character."),
    ],
)
def test_create_account_weak_passwords(client, password, error_detail):
    payload = {"login": "valid_login", "password": password}

    response = client.post("/accounts", json=payload)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert error_detail in response.text


@pytest.mark.parametrize(
    "email",
    [
        "not-an-email",
        "foo@",
        "foo@bar",
        "with space@example.com",
        "",
        "a",
        "foo@.com",
        "@no-local-part.com",
        "user@@domain.com",
    ],
)
def test_create_account_invalid_email(client, email):
    payload = {"email": email, "password": STRONG_PASSWORD}

    response = client.post("/accounts", json=payload)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


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


@pytest.mark.parametrize(
    "data,expected_status",
    [
        ({}, status.HTTP_422_UNPROCESSABLE_ENTITY),
        ({"username": "user"}, status.HTTP_422_UNPROCESSABLE_ENTITY),
        ({"password": STRONG_PASSWORD}, status.HTTP_422_UNPROCESSABLE_ENTITY),
        ({"username": "", "password": STRONG_PASSWORD}, status.HTTP_401_UNAUTHORIZED),
        ({"username": "user", "password": ""}, status.HTTP_401_UNAUTHORIZED),
    ],
)
def test_login_missing_fields(client, mock_log_user, data, expected_status):
    if data.get("username", "") == "" or data.get("password", "") == "":
        mock_log_user.side_effect = UserNotFound()
    with patch("asyncio.sleep", new=AsyncMock()) as mock_sleep:
        response = client.post("/auth/login", data=data)
        if expected_status == status.HTTP_401_UNAUTHORIZED:
            mock_sleep.assert_called()
    assert response.status_code == expected_status


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


def test_refresh_missing_header(client, mock_refresh_token):
    response = client.post("/auth/refresh")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    mock_refresh_token.assert_not_called()


def test_refresh_empty_token(client, mock_refresh_token):
    headers = {"X-Refresh-Token": ""}
    response = client.post("/auth/refresh", headers=headers)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    mock_refresh_token.assert_not_called()


def test_refresh_invalid_token(client, mock_refresh_token, bearer_token_generator):
    invalid_refresh_token = next(bearer_token_generator)
    mock_refresh_token.side_effect = InvalidCredentials()
    headers = {"X-Refresh-Token": invalid_refresh_token}

    response = client.post("/auth/refresh", headers=headers)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Invalid refresh token!"}
    mock_refresh_token.assert_awaited_once_with(invalid_refresh_token, ANY)


async def test_verify_account_success(client, mock_verify_account_email, email_token_generator):
    verification_token = next(email_token_generator)
    response = client.get(f"/accounts/verify/{verification_token}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    mock_verify_account_email.assert_awaited_once_with(
        verification_token, ANY, ANY
    )


async def test_verify_account_invalid_token(client, mock_verify_account_email, email_token_generator):
    verification_token = next(email_token_generator)
    mock_verify_account_email.side_effect = InvalidCredentials()

    response = client.get(f"/accounts/verify/{verification_token}")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Invalid verification token!"}
    mock_verify_account_email.assert_awaited_once_with(
        verification_token, ANY, ANY
    )


@pytest.mark.parametrize(
    "verification_token",
    [
        'zEFGWPDYgwWvmBzqZa9DNnGY8CGhOMbDtmJMZmLwLw',
        'LpWPt8b1-rcaCviPtdoLSZyHNHNKEAxtxe7jEBLuyuwN'
    ],
)
async def test_verify_account_invalid_token_length(client, mock_verify_account_email, verification_token):
    response = client.get(f"/accounts/verify/{verification_token}")

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    mock_verify_account_email.assert_not_awaited()

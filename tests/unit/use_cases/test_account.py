from unittest.mock import ANY, AsyncMock, patch

import pytest
from fastapi import status

from app.shared.exceptions import InvalidCredentials, UserExists
from tests.consts import STRONG_PASSWORD, VALID_EMAIL
from app.shared.settings.application import app_settings

ACCESS_TOKEN_EXPIRATION_SECONDS = app_settings.ACCESS_TOKEN_EXPIRATION_SECONDS
REFRESH_TOKEN_EXPIRATION_SECONDS = app_settings.REFRESH_TOKEN_EXPIRATION_SECONDS


@pytest.fixture
def mock_create_account():
    with patch("app.domain.services.accounts.create_account", new_callable=AsyncMock) as mock_create_account:
        yield mock_create_account


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


async def test_verify_account_success(client, mock_verify_account_email, email_token_generator):
    verification_token = next(email_token_generator)
    response = client.get(f"/accounts/verify/{verification_token}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    mock_verify_account_email.assert_awaited_once_with(verification_token, ANY, ANY)


async def test_verify_account_invalid_token(client, mock_verify_account_email, email_token_generator):
    verification_token = next(email_token_generator)
    mock_verify_account_email.side_effect = InvalidCredentials()

    response = client.get(f"/accounts/verify/{verification_token}")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Invalid verification token!"}
    mock_verify_account_email.assert_awaited_once_with(verification_token, ANY, ANY)

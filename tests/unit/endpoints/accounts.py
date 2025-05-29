import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from app.main import app
from app.core.exceptions import UserExists


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

    assert response.status_code == 201
    mock_users_unit_of_work.assert_awaited_once()


def test_create_account_conflict(client, mock_users_unit_of_work):
    mock_users_unit_of_work.side_effect = UserExists()
    payload = {"login": "existinguser", "password": "StrongPassword1!"}

    response = client.post("/accounts", json=payload)

    assert response.status_code == 409
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

    assert response.status_code == 422
    assert error_detail in response.text


@pytest.mark.parametrize(
    "login",
    ["in valid", "with@symbol", "!", "", "a"]
)
def test_create_account_invalid_login(client, login):
    payload = {"login": login, "password": "ValidPass1!"}

    response = client.post("/accounts", json=payload)

    assert response.status_code == 422

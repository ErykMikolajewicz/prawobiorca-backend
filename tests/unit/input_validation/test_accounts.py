import pytest
from fastapi import status

from tests.consts import STRONG_PASSWORD
from app.framework.dependencies.accounts import create_account_provider, verify_account_provider


@pytest.mark.parametrize(
    "password, error_detail",
    [
        ("nouppercase1!", "Password must contain at least one uppercase letter."),
        ("NOLOWERCASE1!", "Password must contain at least one lowercase letter."),
        ("NoDigits!!", "Password must contain at least one digit."),
        ("NoSpecial1", "Password must contain at least one special character."),
    ],
)
def test_create_account_weak_passwords(client, assure_use_case_not_executed, password, error_detail):
    assure_use_case_not_executed(create_account_provider)

    payload = {"email": "example@example.com", "password": password}

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
def test_create_account_invalid_email(client, assure_use_case_not_executed, email):
    assure_use_case_not_executed(create_account_provider)

    payload = {"email": email, "password": STRONG_PASSWORD}

    response = client.post("/accounts", json=payload)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert '"detail":[{"type":"value_error","loc":["body","email"]' in response.text


@pytest.mark.parametrize(
    "verification_token",
    ["zEFGWPDYgwWvmBzqZa9DNnGY8CGhOMbDtmJMZmLwLw", "LpWPt8b1-rcaCviPtdoLSZyHNHNKEAxtxe7jEBLuyuwN"],
)
async def test_verify_account_invalid_token_length(client, assure_use_case_not_executed, verification_token):
    assure_use_case_not_executed(verify_account_provider)

    response = client.post(f"/accounts/verify/{verification_token}")

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

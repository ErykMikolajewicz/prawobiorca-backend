import pytest

from app.framework.dependencies.accounts import create_account_provider


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

    payload = {"username": "example@example.com", "password": password}

    response = client.post(
        "/accounts/register", data=payload, headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    assert error_detail in response.text

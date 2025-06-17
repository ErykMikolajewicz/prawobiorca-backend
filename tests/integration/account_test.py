from tests.test_consts import VALID_EMAIL, STRONG_PASSWORD


def test_create_account_integration(client, override_get_relational_session):
    payload = {
        "email": VALID_EMAIL,
        "password": STRONG_PASSWORD
    }
    response = client.post("/accounts", json=payload)
    assert response.status_code == 201

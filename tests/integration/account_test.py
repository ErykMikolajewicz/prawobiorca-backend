from fastapi import status

from tests.test_consts import STRONG_PASSWORD, VALID_EMAIL
from app.shared.enums import KeyPrefix


def test_create_account_integration(client, override_get_relational_session):
    payload = {"email": VALID_EMAIL, "password": STRONG_PASSWORD}
    response = client.post("/accounts", json=payload)
    assert response.status_code == status.HTTP_201_CREATED


# async def test_verify_account_email_integration_success(
#     client,
#     override_get_relational_session,
#     email_token_generator,
#     uuid_generator,
#     override_get_key_value_repository
# ):
#     verification_token = next(email_token_generator)
#     user_id = next(uuid_generator)
#     email_verification_key = f"{KeyPrefix.EMAIL_VERIFICATION_TOKEN}:{verification_token}"
#
#     # await redis_client.set(email_verification_key, user_id, ex=3600)
#
#     response = client.get(f"/accounts/verify/{verification_token}")
#     assert response.status_code == status.HTTP_204_NO_CONTENT


async def test_verify_account_email_integration_invalid_token(
    client,
    override_get_relational_session,
    email_token_generator,
    override_get_key_value_repository
):
    invalid_token = next(email_token_generator)

    response = client.get(f"/accounts/verify/{invalid_token}")
    assert response.status_code == status.HTTP_400_BAD_REQUEST

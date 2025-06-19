from fastapi import status

from app.infrastructure.relational_db.repositories.users import UsersRepository
from app.shared.enums import KeyPrefix
from tests.test_consts import STRONG_PASSWORD, VALID_EMAIL


async def test_create_account(client, override_get_relational_session, relational_session):
    payload = {"email": VALID_EMAIL, "password": STRONG_PASSWORD}
    user_repository = UsersRepository(relational_session)

    user = await user_repository.get_by_email(VALID_EMAIL)
    assert user is None

    response = client.post("/accounts", json=payload)
    assert response.status_code == status.HTTP_201_CREATED

    user = await user_repository.get_by_email(VALID_EMAIL)
    try:
        assert user.email == VALID_EMAIL
    finally:
        await user_repository.delete(user.id)


async def test_verify_account_email_success(
    client,
    override_get_relational_session,
    email_token_generator,
    uuid_generator,
    override_get_key_value_repository,
    redis_client,
    relational_session,
):
    verification_token = next(email_token_generator)
    user_id = next(uuid_generator)
    email_verification_key = f"{KeyPrefix.EMAIL_VERIFICATION_TOKEN}:{verification_token}"

    user_repository = UsersRepository(relational_session)
    await user_repository.add({"id": user_id, "email": VALID_EMAIL, "hashed_password": b"", "is_email_verified": False})

    redis_client.set(email_verification_key, user_id, ex=3600)

    response = client.get(f"/accounts/verify/{verification_token}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    user = await user_repository.get_by_email(VALID_EMAIL)
    try:
        assert user.is_email_verified == True
    finally:
        await user_repository.delete(user.id)
        redis_client.delete(email_verification_key)


def test_verify_account_email_integration_invalid_token(
    client, email_token_generator, override_get_key_value_repository
):
    invalid_token = next(email_token_generator)

    response = client.get(f"/accounts/verify/{invalid_token}")
    assert response.status_code == status.HTTP_400_BAD_REQUEST

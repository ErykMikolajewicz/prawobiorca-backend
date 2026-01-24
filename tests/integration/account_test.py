from typing import cast
from uuid import UUID

from fastapi import status

from app.domain.services.security import hash_password
from app.infrastructure.relational_db.repositories.users import UsersRepository
from app.shared.settings.application import app_settings
from app.shared.enums import KeyPrefix, TokenType
from tests.test_consts import STRONG_PASSWORD, VALID_EMAIL
from app.domain.services.security import Secret

ACCESS_TOKEN_EXPIRATION_SECONDS = app_settings.ACCESS_TOKEN_EXPIRATION_SECONDS
REFRESH_TOKEN_EXPIRATION_SECONDS = app_settings.REFRESH_TOKEN_EXPIRATION_SECONDS


async def test_create_account(client, override_get_relational_session, relational_session):
    user_repository = UsersRepository(relational_session)
    user = await user_repository.get_by_email(VALID_EMAIL)
    assert user is None

    payload = {"email": VALID_EMAIL, "password": STRONG_PASSWORD}
    response = client.post("/accounts", json=payload)
    assert response.status_code == status.HTTP_201_CREATED

    user = await user_repository.get_by_email(VALID_EMAIL)
    user_id = cast(UUID, user.id)
    try:
        assert user.email == VALID_EMAIL
    finally:
        await user_repository.delete(user_id)


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

    await redis_client.set(email_verification_key, user_id, ex=3600)

    response = client.post(f"/accounts/verify/{verification_token}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    user = await user_repository.get_by_email(VALID_EMAIL)
    try:
        assert user.is_email_verified == True
    finally:
        await user_repository.delete(user_id)
        await redis_client.delete(email_verification_key)


def test_verify_account_email_integration_invalid_token(
    client, email_token_generator, override_get_key_value_repository
):
    invalid_token = next(email_token_generator)

    response = client.post(f"/accounts/verify/{invalid_token}")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_login_success(
    client,
    uuid_generator,
    override_get_relational_session,
    override_get_key_value_repository,
    relational_session,
    redis_client,
):
    user_id = next(uuid_generator)
    password = Secret(STRONG_PASSWORD)
    hashed_password = hash_password(password)

    user_repository = UsersRepository(relational_session)
    user = await user_repository.add(
        {
            "id": user_id,
            "email": VALID_EMAIL,
            "hashed_password": hashed_password,
            "is_email_verified": True,
        }
    )

    payload = {
        "username": VALID_EMAIL,
        "password": STRONG_PASSWORD,
    }
    response = client.post("/auth/login", data=payload)
    assert response.status_code == status.HTTP_200_OK

    response_json = response.json()
    access_token = response_json["access_token"]
    refresh_token = response_json["refresh_token"]
    try:
        assert response_json["token_type"] == TokenType.BEARER
        assert response_json["expires_in"] == ACCESS_TOKEN_EXPIRATION_SECONDS
    finally:
        await user_repository.delete(user.id)
        await redis_client.delete(
            f"{KeyPrefix.USER_REFRESH_TOKEN}:{user_id}",
            f"{KeyPrefix.REFRESH_TOKEN}:{refresh_token}",
            f"{KeyPrefix.ACCESS_TOKEN}:{access_token}",
        )


async def test_logout_user(client, override_get_key_value_repository, redis_client, uuid_generator, bearer_token_generator):
    user_id = next(uuid_generator)
    access_token = next(bearer_token_generator)
    refresh_token = next(bearer_token_generator)

    await redis_client.set(f"{KeyPrefix.USER_REFRESH_TOKEN}:{user_id}", refresh_token, ex=REFRESH_TOKEN_EXPIRATION_SECONDS)
    await redis_client.set(f"{KeyPrefix.REFRESH_TOKEN}:{refresh_token}", user_id, ex=REFRESH_TOKEN_EXPIRATION_SECONDS)
    await redis_client.set(f"{KeyPrefix.ACCESS_TOKEN}:{access_token}", user_id, ex=ACCESS_TOKEN_EXPIRATION_SECONDS)

    response = client.post("/auth/logout", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == status.HTTP_204_NO_CONTENT

    assert await redis_client.get(f"{KeyPrefix.USER_REFRESH_TOKEN}:{user_id}") is None
    assert await redis_client.get(f"{KeyPrefix.REFRESH_TOKEN}:{refresh_token}") is None
    assert await redis_client.get(f"{KeyPrefix.ACCESS_TOKEN}:{access_token}") is None


async def test_refresh_returns_new_tokens_and_invalidates_old(
    client, redis_client, override_get_key_value_repository, uuid_generator, bearer_token_generator
):
    user_id = next(uuid_generator)
    old_refresh_token = next(bearer_token_generator)

    await redis_client.set(f"{KeyPrefix.REFRESH_TOKEN}:{old_refresh_token}", user_id, ex=REFRESH_TOKEN_EXPIRATION_SECONDS)

    response = client.post("/auth/refresh", headers={"X-Refresh-Token": old_refresh_token})
    assert response.status_code == status.HTTP_200_OK

    response_json = response.json()
    new_refresh_token = response_json["refresh_token"]
    access_token = response_json["access_token"]

    try:
        assert response_json["token_type"] == TokenType.BEARER
        assert response_json["expires_in"] == ACCESS_TOKEN_EXPIRATION_SECONDS
        assert new_refresh_token != old_refresh_token

        assert await redis_client.get(f"{KeyPrefix.REFRESH_TOKEN}:{old_refresh_token}") is None
        assert await redis_client.get(f"{KeyPrefix.REFRESH_TOKEN}:{new_refresh_token}") == user_id
        assert await redis_client.get(f"{KeyPrefix.ACCESS_TOKEN}:{access_token}") == user_id
    finally:
        await redis_client.delete(
            f"{KeyPrefix.REFRESH_TOKEN}:{new_refresh_token}",
            f"{KeyPrefix.ACCESS_TOKEN}:{access_token}",
            f"{KeyPrefix.USER_REFRESH_TOKEN}:{user_id}",
        )

from fastapi import status
from pydantic import SecretStr

from app.domain.services.security import hash_password
from app.framework.dependencies.file_storage import app_settings
from app.infrastructure.relational_db.repositories.users import UsersRepository
from tests.consts import STRONG_PASSWORD, VALID_USERNAME

ACCESS_TOKEN_EXPIRATION_SECONDS = app_settings.ACCESS_TOKEN_EXPIRATION_SECONDS


async def test_create_account(client, override_get_relational_session, relational_session):
    user_repository = UsersRepository(relational_session)
    user = await user_repository.get_by_username(VALID_USERNAME)
    assert user is None

    payload = {"username": VALID_USERNAME, "password": STRONG_PASSWORD}
    response = client.post("/accounts", json=payload)
    assert response.status_code == status.HTTP_201_CREATED

    user = await user_repository.get_by_username(VALID_USERNAME)
    user_id = user.id
    try:
        assert user.username == VALID_USERNAME
    finally:
        # TODO implement deleting user
        await user_repository.delete(user_id)


async def test_login_success(client, uuid_generator, override_get_relational_session, relational_session):
    user_id = next(uuid_generator)
    password = SecretStr(STRONG_PASSWORD)
    hashed_password = hash_password(password)

    user_repository = UsersRepository(relational_session)
    # TODO use dataclass
    await user_repository.add(
        {
            "id": user_id,
            "email": VALID_USERNAME,
            "hashed_password": hashed_password,
            "is_email_verified": True,
        }
    )

    payload = {
        "username": VALID_USERNAME,
        "password": STRONG_PASSWORD,
    }
    response = client.post("/auth/login", data=payload)
    assert response.status_code == status.HTTP_200_OK

    response_json = response.json()
    # session_id = response_json["session_id"]
    try:
        assert response_json["expires_in"] == ACCESS_TOKEN_EXPIRATION_SECONDS
    finally:
        pass
        # TODO delete session

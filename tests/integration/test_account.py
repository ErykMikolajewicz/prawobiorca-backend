from fastapi import status
from pydantic import SecretStr

from app.domain.services.security import hash_password
from app.domain.value_objects.user import CreateUserData
from app.framework.dependencies.file_storage import app_settings
from app.infrastructure.relational_db.repositories.users import UsersRepository
from app.infrastructure.relational_db.schemas.users import UsersTokens
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
    try:
        assert user.username == VALID_USERNAME
    finally:
        await relational_session.delete(user)
        await relational_session.commit()


async def test_login_success(client, override_get_relational_session, relational_session):
    password = SecretStr(STRONG_PASSWORD)
    hashed_password = hash_password(password)

    user_repository = UsersRepository(relational_session)
    user_data = CreateUserData(username=VALID_USERNAME, hashed_password=hashed_password)
    await user_repository.add(user_data)

    payload = {
        "username": VALID_USERNAME,
        "password": STRONG_PASSWORD,
    }
    response = client.post("/auth/login", data=payload)
    assert response.status_code == status.HTTP_200_OK

    response_json = response.json()
    session_id = response_json["session_id"]
    try:
        assert response_json["expires_in"] == ACCESS_TOKEN_EXPIRATION_SECONDS
    finally:
        user_token = await relational_session.get(UsersTokens, session_id)
        await relational_session.delete(user_token)
        await relational_session.commit()

import json
from http.cookies import SimpleCookie

from fastapi import status
from pydantic import SecretStr
from sqlalchemy import delete

from app.domain.services.security import hash_password
from app.domain.value_objects.user import CreateUserData
from app.framework.dependencies.file_storage import app_settings
from app.infrastructure.relational_db.repositories.users import UsersRepository
from app.infrastructure.relational_db.schemas.users import Users, UsersTokens
from app.shared.consts import AUTHORIZATION_COOKIE_NAME
from tests.consts import STRONG_PASSWORD, VALID_USERNAME

SESSION_ID_EXPIRATION_SECONDS = app_settings.SESSION_ID_EXPIRATION_SECONDS


async def test_create_account(client, override_session_maker, session_maker):
    async with session_maker() as session:
        user_repository = UsersRepository()
        user = await user_repository.get_by_username(session, VALID_USERNAME)
        assert user is None

    payload = {"username": VALID_USERNAME, "password": STRONG_PASSWORD}
    response = client.post("/api/accounts/register", json=payload)
    assert response.status_code == status.HTTP_201_CREATED

    async with session_maker.begin() as session:
        user = await user_repository.get_by_username(session, VALID_USERNAME)
        assert user is not None
        try:
            assert user.username == VALID_USERNAME
        finally:
            statement = delete(Users).where(Users.username == user.username)
            await session.execute(statement)


async def test_login_success(client, override_session_maker, session_maker):
    password = SecretStr(STRONG_PASSWORD)
    hashed_password = hash_password(password)

    async with session_maker.begin() as session:
        user_repository = UsersRepository()
        user_data = CreateUserData(
            username=VALID_USERNAME,
            hashed_password=hashed_password,
        )
        await user_repository.add(session, user_data)

    payload = {
        "username": VALID_USERNAME,
        "password": STRONG_PASSWORD,
    }

    response = client.post("/api/auth/login", json=payload)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"ok": True}

    set_cookie_header = response.headers["set-cookie"]

    cookies = SimpleCookie()
    cookies.load(set_cookie_header)

    cookie_value = cookies[AUTHORIZATION_COOKIE_NAME].value
    session_data = json.loads(cookie_value)

    session_id = session_data["session_id"]

    assert session_data["expires_in"] == SESSION_ID_EXPIRATION_SECONDS

    async with session_maker.begin() as session:
        user_token = await session.get(UsersTokens, session_id)
        assert user_token is not None
        await session.delete(user_token)

from datetime import datetime, timedelta, timezone
from http.cookies import SimpleCookie

from fastapi import status
from sqlalchemy import delete, select

from app.infrastructure.relational_db.repositories.users import UsersRepository, UsersTokensRepository
from app.infrastructure.relational_db.schemas.users import users_tokens_table
from app.shared.consts import AUTHORIZATION_COOKIE_NAME
from app.shared.settings.application import app_settings
from tests.consts import AUTHORIZATION_TOKEN, STRONG_PASSWORD, USER_ID, VALID_USERNAME

SESSION_ID_EXPIRATION_SECONDS = app_settings.SESSION_ID_EXPIRATION_SECONDS


async def test_create_account(client, override_session_maker, session_maker, clean_user):
    async with session_maker() as session:
        user_repository = UsersRepository()
        user = await user_repository.get_by_username(session, VALID_USERNAME)
        assert user is None

    payload = {"username": VALID_USERNAME, "password": STRONG_PASSWORD}
    response = client.post("/api/accounts/register", json=payload)
    assert response.status_code == status.HTTP_201_CREATED

    async with session_maker() as session:
        user = await user_repository.get_by_username(session, VALID_USERNAME)
    assert user is not None
    assert user.username == VALID_USERNAME


async def test_login_success(client, override_session_maker, session_maker, set_user, clean_user):
    payload = {
        "username": VALID_USERNAME,
        "password": STRONG_PASSWORD,
    }

    response = client.post("/api/auth/login", data=payload)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"ok": True}

    set_cookie_header = response.headers["set-cookie"]

    cookies = SimpleCookie()
    cookies.load(set_cookie_header)

    authorization_token = cookies[AUTHORIZATION_COOKIE_NAME].value

    assert int(cookies[AUTHORIZATION_COOKIE_NAME]["max-age"]) == SESSION_ID_EXPIRATION_SECONDS

    async with session_maker.begin() as session:
        statement = select(users_tokens_table).where(users_tokens_table.c.session_id == authorization_token)
        user_token = await session.scalar(statement)
        assert user_token is not None
        statement = delete(users_tokens_table).where(users_tokens_table.c.session_id == authorization_token)
        await session.execute(statement)


async def test_login_failure_wrong_password(client, override_session_maker, session_maker, set_user, clean_user):
    payload = {
        "username": VALID_USERNAME,
        "password": "WrongPassword123!",
    }

    response = client.post("/api/auth/login", data=payload)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "incorrect logging data!"}


async def test_logout_success(client, override_session_maker, session_maker, set_user, clean_user):
    valid_until = datetime.now(timezone.utc) + timedelta(seconds=SESSION_ID_EXPIRATION_SECONDS)

    async with session_maker.begin() as session:
        users_tokens_repository = UsersTokensRepository()
        await users_tokens_repository.add_token(session, USER_ID, AUTHORIZATION_TOKEN, valid_until)

    client.cookies.set(AUTHORIZATION_COOKIE_NAME, AUTHORIZATION_TOKEN)

    logout_response = client.post("/api/auth/logout")

    assert logout_response.status_code == status.HTTP_200_OK
    assert logout_response.json() == {"ok": True}

    set_cookie_header_logout = logout_response.headers.get("set-cookie")
    assert set_cookie_header_logout is not None
    assert "Max-Age=0" in set_cookie_header_logout or "expires=" in set_cookie_header_logout.lower()

    async with session_maker.begin() as session:
        statement = select(users_tokens_table).where(users_tokens_table.c.session_id == AUTHORIZATION_TOKEN)
        user_token = await session.scalar(statement)
    assert user_token is None

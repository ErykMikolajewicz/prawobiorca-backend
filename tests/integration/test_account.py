import json
from datetime import datetime, timedelta, timezone
from http.cookies import SimpleCookie

from fastapi import status
from pydantic import SecretStr
from sqlalchemy import delete

from app.domain.services.security import hash_password
from app.domain.value_objects.user import CreateUserData
from app.framework.dependencies.file_storage import app_settings
from app.infrastructure.relational_db.repositories.users import UsersRepository, UsersTokensRepository
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

    try:
        async with session_maker() as session:
            user = await user_repository.get_by_username(session, VALID_USERNAME)
        assert user is not None
        assert user.username == VALID_USERNAME
    except Exception:
        raise
    finally:
        statement = delete(Users).where(Users.username == VALID_USERNAME)
        async with session_maker.begin() as session:
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

    try:
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
    except Exception:
        raise
    finally:
        async with session_maker.begin() as session:
            statement = delete(Users).where(Users.username == VALID_USERNAME)
            await session.execute(statement)


async def test_login_failure_wrong_password(client, override_session_maker, session_maker):
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
        "password": "WrongPassword123!",
    }

    try:
        response = client.post("/api/auth/login", json=payload)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": "incorrect logging data!"}
    except Exception:
        raise
    finally:
        async with session_maker.begin() as session:
            statement = delete(Users).where(Users.username == VALID_USERNAME)
            await session.execute(statement)


async def test_logout_success(client, override_session_maker, session_maker):
    password = SecretStr(STRONG_PASSWORD)
    hashed_password = hash_password(password)

    session_id = "QcC42nmGS1kkCkLix4koy79tOjf6aSZKZNv_4KYkNfT-CQGU8vvlB_59og"
    valid_until = datetime.now(timezone.utc) + timedelta(seconds=SESSION_ID_EXPIRATION_SECONDS)

    async with session_maker.begin() as session:
        user_repository = UsersRepository()
        user_data = CreateUserData(
            username=VALID_USERNAME,
            hashed_password=hashed_password,
        )
        await user_repository.add(session, user_data)
        user = await user_repository.get_by_username(session, VALID_USERNAME)
        user_id = user.id

        users_tokens_repository = UsersTokensRepository()
        await users_tokens_repository.add_session(session, user_id, session_id, valid_until)

    try:
        client.cookies.set(
            "session_data",
            json.dumps({"session_id": session_id}),
        )

        logout_response = client.post("/api/auth/logout")

        assert logout_response.status_code == status.HTTP_200_OK
        assert logout_response.json() == {"ok": True}

        set_cookie_header_logout = logout_response.headers.get("set-cookie")
        assert set_cookie_header_logout is not None
        assert "Max-Age=0" in set_cookie_header_logout or "expires=" in set_cookie_header_logout.lower()

        async with session_maker.begin() as session:
            user_token = await session.get(UsersTokens, session_id)
            assert user_token is None
    except Exception:
        raise
    finally:
        async with session_maker.begin() as session:
            statement = delete(Users).where(Users.username == VALID_USERNAME)
            await session.execute(statement)

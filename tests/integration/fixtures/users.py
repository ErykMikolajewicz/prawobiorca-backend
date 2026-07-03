from pydantic import SecretStr
from pytest import fixture
from sqlalchemy import delete, insert

from app.domain.services.security import hash_password
from app.infrastructure.relational_db.schemas.users import Users
from tests.consts import ADMIN_ID, ADMIN_USERNAME, STRONG_PASSWORD, USER_ID, VALID_USERNAME


@fixture(scope="function")
async def set_user(session_maker):
    password = SecretStr(STRONG_PASSWORD)
    hashed_password = hash_password(password)

    async with session_maker.begin() as session:
        statement = insert(Users).values(id=USER_ID, username=VALID_USERNAME, hashed_password=hashed_password)
        await session.execute(statement)

    yield


@fixture(scope="function")
async def clean_user(session_maker):
    yield
    async with session_maker.begin() as session:
        statement = delete(Users).where(Users.username == VALID_USERNAME)
        await session.execute(statement)


@fixture(scope="function")
async def set_admin_user(session_maker):
    password = SecretStr(STRONG_PASSWORD)
    hashed_password = hash_password(password)

    async with session_maker.begin() as session:
        statement = insert(Users).values(
            id=ADMIN_ID, username=ADMIN_USERNAME, hashed_password=hashed_password, is_admin=True
        )
        await session.execute(statement)

    yield


@fixture(scope="function")
async def clean_admin_user(session_maker):
    yield
    async with session_maker.begin() as session:
        statement = delete(Users).where(Users.username == ADMIN_USERNAME)
        await session.execute(statement)

from fastapi import status

from app.infrastructure.relational_db.repositories.users import UsersRepository
from tests.consts import STRONG_PASSWORD, VALID_USERNAME


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

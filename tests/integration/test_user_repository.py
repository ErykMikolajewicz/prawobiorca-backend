from pydantic import SecretStr

from app.domain.services.security import hash_password
from app.domain.value_objects.user import CreateUserData
from app.infrastructure.relational_db.repositories.users import UsersRepository
from tests.consts import STRONG_PASSWORD, VALID_USERNAME


async def test_get_by_id(session_maker):
    hashed_password = hash_password(SecretStr(STRONG_PASSWORD))

    user_data = CreateUserData(username=VALID_USERNAME, hashed_password=hashed_password, is_admin=True)

    user_repo = UsersRepository()

    async with session_maker.begin() as session:
        await user_repo.add(session, user_data)

    async with session_maker() as session:
        created_user = await user_repo.get_by_username(session, user_data.username)

        assert created_user is not None
        assert created_user.is_admin is True

        found_user = await user_repo.get_by_id(session, created_user.id)

    assert found_user is not None
    assert found_user.is_admin is True

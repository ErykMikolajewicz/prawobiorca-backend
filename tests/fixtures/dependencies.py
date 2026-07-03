from enum import StrEnum
from typing import Callable

import pytest
from fastapi.requests import Request

from app.domain.services.security import extract_authorization_token
from app.domain.value_objects.users import UserPrivileges
from app.framework.dependencies.authentication import authorize_user
from app.framework.dependencies.regulations import get_regulations_repository
from app.shared.consts import AUTHORIZATION_COOKIE_NAME
from main import prawobiorca
from tests.consts import AUTHORIZATION_TOKEN, USER_ID


class MockStorageRepository:
    async def upload_file(self, file_data):
        pass


@pytest.fixture
def override_get_public_file_storage():
    prawobiorca.dependency_overrides[get_regulations_repository] = lambda: MockStorageRepository()
    yield
    prawobiorca.dependency_overrides = {}


class UserType(StrEnum):
    NORMAL = "NORMAL"
    ADMIN = "ADMIN"


@pytest.fixture
def get_set_mock_auth_dependency(uuid_generator) -> Callable:

    def set_mock_auth_dependency(user_type: UserType):
        async def mock_authorize_user(request: Request):
            authorization_data = request.cookies.get(AUTHORIZATION_COOKIE_NAME)
            authorization_token = extract_authorization_token(authorization_data)

            user_id = None
            user_privileges = None
            if authorization_token == AUTHORIZATION_TOKEN:
                user_id = USER_ID
                match user_type:
                    case UserType.NORMAL:
                        user_privileges = UserPrivileges(is_admin=False)
                    case UserType.ADMIN:
                        user_privileges = UserPrivileges(is_admin=True)
                    case _:
                        raise Exception("Invalid user type!")

            request.state.authorization_token = authorization_token
            request.state.user_id = user_id
            request.state.user_privileges = user_privileges

        return mock_authorize_user

    return set_mock_auth_dependency


@pytest.fixture
def override_authorize_normal_user(get_set_mock_auth_dependency):
    override_function = get_set_mock_auth_dependency(UserType.NORMAL)
    prawobiorca.dependency_overrides[authorize_user] = override_function
    yield
    prawobiorca.dependency_overrides.pop(authorize_user, None)


@pytest.fixture
def override_authorize_admin_user(get_set_mock_auth_dependency):
    override_function = get_set_mock_auth_dependency(UserType.ADMIN)
    prawobiorca.dependency_overrides[authorize_user] = override_function
    yield
    prawobiorca.dependency_overrides.pop(authorize_user, None)

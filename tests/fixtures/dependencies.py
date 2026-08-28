from enum import StrEnum
from typing import Callable
from unittest.mock import create_autospec

import pytest
from fastapi.requests import Request

from app.application.interfaces.regulations import RegulationsStorage
from app.application.ports.tasks import RegulationPreparationScheduler
from app.domain.value_objects.users import UserPrivileges
from app.framework.dependencies.authentication import authorize_user
from app.framework.dependencies.regulations import get_regulations_preparation_scheduler, get_regulations_storage
from app.shared.consts import AUTHORIZATION_COOKIE_NAME
from main import prawobiorca
from tests.consts import AUTHORIZATION_TOKEN, USER_ID


@pytest.fixture
def mock_regulations_storage():
    return create_autospec(RegulationsStorage)


@pytest.fixture
def override_get_regulations_storage(mock_regulations_storage):
    prawobiorca.dependency_overrides[get_regulations_storage] = lambda: mock_regulations_storage
    yield
    prawobiorca.dependency_overrides.pop(get_regulations_storage, None)


@pytest.fixture
def mock_regulation_preparation_scheduler():
    return create_autospec(RegulationPreparationScheduler)


@pytest.fixture
def override_get_regulations_preparation_scheduler(mock_regulation_preparation_scheduler):
    prawobiorca.dependency_overrides[get_regulations_preparation_scheduler] = lambda: (
        mock_regulation_preparation_scheduler
    )
    yield
    prawobiorca.dependency_overrides.pop(get_regulations_preparation_scheduler, None)


class UserType(StrEnum):
    NORMAL = "NORMAL"
    ADMIN = "ADMIN"


@pytest.fixture
def get_set_mock_auth_dependency() -> Callable:

    def set_mock_auth_dependency(user_type: UserType):
        async def mock_authorize_user(request: Request):
            authorization_token = request.cookies.get(AUTHORIZATION_COOKIE_NAME)

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

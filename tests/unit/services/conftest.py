from unittest.mock import AsyncMock
from uuid import UUID, uuid4

import pytest

from tests.consts import VALID_USERNAME


class DummyUser:
    def __init__(self, id_: UUID, username: str, hashed_password: bytes):
        self.id = id_
        self.username = username
        self.hashed_password = hashed_password


class DummyAsyncContextManager:
    def __init__(self, return_object):
        self.return_object = return_object

    async def __aenter__(self):
        return self.return_object

    async def __aexit__(self, exc_type, exc, tb):
        return None


@pytest.fixture
def user():
    return DummyUser(id_=uuid4(), username=VALID_USERNAME, hashed_password=b"hashed")


@pytest.fixture
def storage_client():
    return AsyncMock()

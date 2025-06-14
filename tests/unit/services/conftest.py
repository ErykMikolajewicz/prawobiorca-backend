from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest


class DummyUser:
    def __init__(self, id_, login, hashed_password):
        self.id = id_
        self.login = login
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
    return DummyUser(id_=uuid4(), login="test_user", hashed_password=b"hashed")


@pytest.fixture
def uow():
    uow = AsyncMock()
    uow.__aenter__.return_value = uow
    return uow


@pytest.fixture
def key_value_repository():
    repo = AsyncMock()
    pipeline = AsyncMock()

    repo.pipeline = lambda: DummyAsyncContextManager(pipeline)
    return repo, pipeline


@pytest.fixture
def storage_client():
    return MagicMock()

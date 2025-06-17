from unittest.mock import AsyncMock
from uuid import UUID, uuid4

import pytest

from tests.test_consts import VALID_EMAIL


class DummyUser:
    def __init__(self, id_: UUID, email: str, hashed_password: bytes, is_email_verified: bool):
        self.id = id_
        self.email = email
        self.hashed_password = hashed_password
        self.is_email_verified = is_email_verified


class DummyAsyncContextManager:
    def __init__(self, return_object):
        self.return_object = return_object

    async def __aenter__(self):
        return self.return_object

    async def __aexit__(self, exc_type, exc, tb):
        return None


@pytest.fixture
def user():
    return DummyUser(id_=uuid4(), email=VALID_EMAIL, hashed_password=b"hashed", is_email_verified=False)


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
    return AsyncMock()

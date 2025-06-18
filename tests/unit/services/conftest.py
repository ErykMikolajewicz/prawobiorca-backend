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


class DummyUnitOfWork:
    def __init__(self, return_object):
        self.return_object = return_object

    async def __aenter__(self):
        return self.return_object

    async def __aexit__(self, exc_type, exc, tb):
        if exc_type is None:
            await self.return_object.commit()
        else:
            await self.return_object.rollback()


@pytest.fixture
def user():
    return DummyUser(id_=uuid4(), email=VALID_EMAIL, hashed_password=b"hashed", is_email_verified=False)


@pytest.fixture
def uow():
    mock_uow = AsyncMock()
    async def aenter_mock(self):
        return self

    async def aexit_mock(self, exc_type, exc, tb):
        if exc_type is None:
            await self.commit()
        else:
            await self.rollback()

    mock_uow.__aenter__ = aenter_mock
    mock_uow.__aexit__ = aexit_mock

    return mock_uow


@pytest.fixture
def key_value_repository():
    repo = AsyncMock()
    pipeline = AsyncMock()

    repo.pipeline = lambda: DummyAsyncContextManager(pipeline)
    return repo, pipeline


@pytest.fixture
def storage_client():
    return AsyncMock()

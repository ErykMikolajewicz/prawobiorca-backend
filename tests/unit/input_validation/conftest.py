import pytest
from fastapi import Request

from app.framework.dependencies.authentication import set_user_by_session_id
from app.framework.dependencies.regulations import get_regulations_repository
from main import prawobiorca


@pytest.fixture
def override_set_user_by_session_id(session_id_generator, uuid_generator):
    def _override(request: Request):
        request.state.user_id = next(uuid_generator)
        request.state.session_id = next(session_id_generator)

    prawobiorca.dependency_overrides[set_user_by_session_id] = _override
    yield
    prawobiorca.dependency_overrides = {}


class MockStorageRepository:
    async def upload_file(self, file_data):
        pass


@pytest.fixture
def override_get_public_file_storage():
    prawobiorca.dependency_overrides[get_regulations_repository] = lambda: MockStorageRepository()
    yield
    prawobiorca.dependency_overrides = {}

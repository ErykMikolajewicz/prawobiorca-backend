import pytest
from fastapi import Request

from app.framework.dependencies.authentication import set_user_by_session_id
from main import app


@pytest.fixture
def override_set_user_by_session_id(session_id_generator, uuid_generator):
    def _override(request: Request):
        request.state.user_id = next(uuid_generator)
        request.state.session_id = next(session_id_generator)

    app.dependency_overrides[set_user_by_session_id] = _override
    yield
    app.dependency_overrides = {}

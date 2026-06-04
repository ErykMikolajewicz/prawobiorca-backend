from unittest.mock import AsyncMock, MagicMock

import pytest


@pytest.fixture
def mock_session():
    session = MagicMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    session.commit = AsyncMock()
    return session


@pytest.fixture
def mock_session_maker(mock_session):
    session_maker = MagicMock()
    session_maker.begin.return_value = mock_session
    return session_maker


@pytest.fixture
def mock_users_repo():
    repo = MagicMock()
    repo.add = AsyncMock()
    return repo


@pytest.fixture
def mock_tokens_repo():
    repo = MagicMock()
    repo.add_session = AsyncMock()
    repo.invalidate_session = AsyncMock()
    return repo


@pytest.fixture
def mock_files_repo():
    repo = MagicMock()
    repo.upload_file = AsyncMock()
    repo.list_files = AsyncMock()
    return repo


@pytest.fixture
def mock_embedding_port():
    port = MagicMock()
    port.embed_queries = AsyncMock()
    port.embed_documents = AsyncMock()
    return port


@pytest.fixture
def mock_documents_repo():
    repo = MagicMock()
    repo.search = AsyncMock()
    repo.add_point = AsyncMock()
    return repo

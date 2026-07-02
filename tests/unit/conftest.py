from unittest.mock import create_autospec

import pytest

from app.application.interfaces.documents import DocumentsRepository
from app.application.interfaces.regulations import RegulationsRepository
from app.application.interfaces.relational import AsyncSession, SessionMaker
from app.application.interfaces.users import UsersRepository, UsersTokensRepository
from app.application.ports.texts import TextsEmbedder
from app.application.use_cases.regulations import AddRegulation


@pytest.fixture
async def mock_session():
    session = create_autospec(AsyncSession)
    opened_session = await session.__aenter__()
    return opened_session


@pytest.fixture
async def mock_opened_session(mock_session):
    opened_session = await mock_session.__aenter__()
    return opened_session


@pytest.fixture
def mock_session_maker(mock_session):
    session_maker = create_autospec(SessionMaker)
    session_maker.begin.return_value = mock_session
    session_maker.return_value = mock_session
    return session_maker


@pytest.fixture
def mock_users_repo():
    repo = create_autospec(UsersRepository)
    return repo


@pytest.fixture
def mock_tokens_repo():
    repo = create_autospec(UsersTokensRepository)
    return repo


@pytest.fixture
def mock_regulations_repo():
    repo = create_autospec(RegulationsRepository)
    return repo


@pytest.fixture
def mock_embedding_port():
    port = create_autospec(TextsEmbedder)
    return port


@pytest.fixture
def mock_documents_repo():
    repo = create_autospec(DocumentsRepository)
    return repo


@pytest.fixture
def mock_add_regulation():
    add_regulation = create_autospec(AddRegulation, instance=True)
    return add_regulation

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from app.infrastructure.relational_db.repositories.regulations import RegulationsManagerRepository


async def test_mark_as_prepared_callable_from_instance():
    session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one.return_value = uuid4()
    session.execute.return_value = mock_result

    repo = RegulationsManagerRepository()
    user_id = uuid4()
    regulation_id = uuid4()

    await repo.mark_as_prepared(session, user_id, regulation_id)

    session.execute.assert_awaited_once()


async def test_mark_as_uploaded_callable_from_instance():
    session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one.return_value = uuid4()
    session.execute.return_value = mock_result

    repo = RegulationsManagerRepository()
    user_id = uuid4()
    regulation_id = uuid4()

    await repo.mark_as_uploaded(session, user_id, regulation_id)

    session.execute.assert_awaited_once()

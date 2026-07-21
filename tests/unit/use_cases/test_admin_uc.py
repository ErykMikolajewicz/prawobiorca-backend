from unittest.mock import AsyncMock, Mock

import pytest

from app.domain.value_objects.regulations import RegulationType
from app.framework.api.endpoints.public_regulations import add_public_regulation


@pytest.mark.asyncio
async def test_add_public_regulation_success(mock_add_regulation, uuid_generator):
    regulation_id = next(uuid_generator)
    mock_add_regulation.execute.return_value = regulation_id

    regulation = Mock()

    regulation.filename = "regulation.pdf"
    regulation.read = AsyncMock(return_value=b"content")

    result = await add_public_regulation(
        add_regulation_=mock_add_regulation, regulation=regulation, regulation_type=RegulationType.ACT
    )

    mock_add_regulation.execute.assert_awaited_once()
    call_args = mock_add_regulation.execute.await_args.kwargs

    assert call_args["user_id"] is None
    assert call_args["regulation_data"].name == "regulation.pdf"
    assert call_args["regulation_data"].file == b"content"
    assert call_args["regulation_data"].regulation_type == RegulationType.ACT

    assert result == regulation_id

import pytest

from app.application.dtos.regulations import RegulationData
from app.application.use_cases.regulations import AddRegulation
from app.domain.value_objects.regulations import RegulationType


@pytest.mark.asyncio
async def test_add_public_regulation_success(
    uuid_generator, mock_regulations_repository, mock_regulations_storage, mock_session_maker
):
    regulation_id = next(uuid_generator)
    mock_regulations_repository.register_regulation.return_value = regulation_id

    regulation_data = RegulationData(name="regulation.pdf", file=b"content", regulation_type=RegulationType.ACT)

    add_regulation = AddRegulation(
        regulations_repository=mock_regulations_repository,
        regulation_storage=mock_regulations_storage,
        session_maker=mock_session_maker,
    )

    result = await add_regulation.execute(user_id=None, regulation_data=regulation_data)

    assert result == regulation_id

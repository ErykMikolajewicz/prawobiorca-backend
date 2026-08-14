from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.dtos.regulations import RegulationData, RegulationRepresentation, RegulationUploadTarget
from app.application.dtos.search import SearchParams
from app.application.use_cases.regulations import (
    AddRegulation,
    ConfirmRegulationUpload,
    DeleteRegulation,
    GetRegulationDownloadUrl,
    GetRegulationUploadTarget,
    ListRegulations,
    PrepareRegulation,
    SearchRegulation,
)
from app.domain.exceptions.documents import RegulationDocumentsNotFound
from app.domain.exceptions.regulations import (
    RegulationAlreadyInitialized,
    RegulationContentNotFound,
    RegulationInInvalidState,
    RegulationNotFound,
    RegulationServiceUnavailable,
    RegulationsNotPreparedToSearch,
)
from app.domain.value_objects.regulations import RegulationType

# --- PrepareRegulation Tests ---


@pytest.mark.asyncio
async def test_prepare_regulation_success(
    mock_session_maker,
    mock_regulations_repository,
    mock_regulations_storage,
    mock_documents_repo,
    uuid_generator,
):
    user_id = next(uuid_generator)
    regulation_id = next(uuid_generator)

    regulation_rep = MagicMock()
    regulation_rep.is_prepared = False
    mock_regulations_repository.get_regulation_representation.return_value = regulation_rep

    mock_regulations_storage.get_regulation.return_value = b"content"

    mock_regulation_preparator = AsyncMock()
    mock_regulation_preparator.prepare_regulation.return_value = ["doc1", "doc2"]

    use_case = PrepareRegulation(
        session_maker=mock_session_maker,
        regulations_storage=mock_regulations_storage,
        documents_repository=mock_documents_repo,
        regulations_repository=mock_regulations_repository,
        regulation_preparator=mock_regulation_preparator,
    )

    await use_case.execute(user_id, regulation_id)

    mock_regulations_repository.get_regulation_representation.assert_awaited_once()
    mock_regulations_storage.get_regulation.assert_awaited_once_with(regulation_id)
    mock_regulation_preparator.prepare_regulation.assert_awaited_once_with(b"content")
    mock_documents_repo.add_documents.assert_awaited_once()
    mock_regulations_repository.mark_as_prepared.assert_awaited_once()


@pytest.mark.asyncio
async def test_prepare_regulation_not_found(
    mock_session_maker,
    mock_regulations_repository,
    mock_regulations_storage,
    mock_documents_repo,
    uuid_generator,
):
    user_id = next(uuid_generator)
    regulation_id = next(uuid_generator)

    mock_regulations_repository.get_regulation_representation.return_value = None

    mock_regulation_preparator = AsyncMock()

    use_case = PrepareRegulation(
        session_maker=mock_session_maker,
        regulations_storage=mock_regulations_storage,
        documents_repository=mock_documents_repo,
        regulations_repository=mock_regulations_repository,
        regulation_preparator=mock_regulation_preparator,
    )

    with pytest.raises(RegulationNotFound):
        await use_case.execute(user_id, regulation_id)


@pytest.mark.asyncio
async def test_prepare_regulation_already_initialized(
    mock_session_maker,
    mock_regulations_repository,
    mock_regulations_storage,
    mock_documents_repo,
    uuid_generator,
):
    user_id = next(uuid_generator)
    regulation_id = next(uuid_generator)

    regulation_rep = MagicMock()
    regulation_rep.is_prepared = True
    mock_regulations_repository.get_regulation_representation.return_value = regulation_rep

    mock_regulation_preparator = AsyncMock()

    use_case = PrepareRegulation(
        session_maker=mock_session_maker,
        regulations_storage=mock_regulations_storage,
        documents_repository=mock_documents_repo,
        regulations_repository=mock_regulations_repository,
        regulation_preparator=mock_regulation_preparator,
    )

    with pytest.raises(RegulationAlreadyInitialized):
        await use_case.execute(user_id, regulation_id)


@pytest.mark.asyncio
async def test_prepare_regulation_content_not_found(
    mock_session_maker,
    mock_regulations_repository,
    mock_regulations_storage,
    mock_documents_repo,
    uuid_generator,
):
    user_id = next(uuid_generator)
    regulation_id = next(uuid_generator)

    regulation_rep = MagicMock()
    regulation_rep.is_prepared = False
    mock_regulations_repository.get_regulation_representation.return_value = regulation_rep

    mock_regulations_storage.get_regulation.side_effect = RegulationContentNotFound

    mock_regulation_preparator = AsyncMock()

    use_case = PrepareRegulation(
        session_maker=mock_session_maker,
        regulations_storage=mock_regulations_storage,
        documents_repository=mock_documents_repo,
        regulations_repository=mock_regulations_repository,
        regulation_preparator=mock_regulation_preparator,
    )

    with pytest.raises(RegulationContentNotFound):
        await use_case.execute(user_id, regulation_id)


@pytest.mark.asyncio
async def test_prepare_regulation_service_unavailable(
    mock_session_maker,
    mock_regulations_repository,
    mock_regulations_storage,
    mock_documents_repo,
    uuid_generator,
):
    user_id = next(uuid_generator)
    regulation_id = next(uuid_generator)

    regulation_rep = MagicMock()
    regulation_rep.is_prepared = False
    mock_regulations_repository.get_regulation_representation.return_value = regulation_rep

    mock_regulations_storage.get_regulation.return_value = b"content"

    mock_regulation_preparator = AsyncMock()
    mock_regulation_preparator.prepare_regulation.side_effect = Exception("Service Down")

    use_case = PrepareRegulation(
        session_maker=mock_session_maker,
        regulations_storage=mock_regulations_storage,
        documents_repository=mock_documents_repo,
        regulations_repository=mock_regulations_repository,
        regulation_preparator=mock_regulation_preparator,
    )

    with pytest.raises(RegulationServiceUnavailable):
        await use_case.execute(user_id, regulation_id)


# --- AddRegulation Tests ---


@pytest.mark.asyncio
async def test_add_public_regulation_success(uuid_generator, mock_regulations_repository, mock_session_maker):
    regulation_id = next(uuid_generator)
    mock_regulations_repository.register_regulation.return_value = regulation_id

    regulation_data = RegulationData(name="regulation.pdf", regulation_type=RegulationType.ACT)

    add_regulation = AddRegulation(
        regulations_repository=mock_regulations_repository,
        session_maker=mock_session_maker,
    )

    result = await add_regulation.execute(user_id=None, regulation_data=regulation_data)

    assert result == regulation_id
    mock_regulations_repository.register_regulation.assert_awaited_once()


# --- GetRegulationUploadTarget Tests ---


@pytest.mark.asyncio
async def test_get_regulation_upload_target_success(
    uuid_generator, mock_regulations_repository, mock_regulations_storage, mock_session_maker
):
    user_id = next(uuid_generator)
    regulation_id = next(uuid_generator)

    regulation_rep = MagicMock()
    regulation_rep.is_prepared = False
    mock_regulations_repository.get_regulation_representation.return_value = regulation_rep

    upload_target = RegulationUploadTarget(url="http://object-storage", fields={"key": str(regulation_id)})
    mock_regulations_storage.get_upload_target.return_value = upload_target

    use_case = GetRegulationUploadTarget(
        session_maker=mock_session_maker,
        regulations_repository=mock_regulations_repository,
        regulations_storage=mock_regulations_storage,
    )

    result = await use_case.execute(user_id, regulation_id)

    assert result == upload_target
    mock_regulations_storage.get_upload_target.assert_awaited_once_with(regulation_id)


@pytest.mark.asyncio
async def test_get_regulation_upload_target_not_found(
    uuid_generator, mock_regulations_repository, mock_regulations_storage, mock_session_maker
):
    user_id = next(uuid_generator)
    regulation_id = next(uuid_generator)

    mock_regulations_repository.get_regulation_representation.return_value = None

    use_case = GetRegulationUploadTarget(
        session_maker=mock_session_maker,
        regulations_repository=mock_regulations_repository,
        regulations_storage=mock_regulations_storage,
    )

    with pytest.raises(RegulationNotFound):
        await use_case.execute(user_id, regulation_id)


@pytest.mark.asyncio
async def test_get_regulation_upload_target_already_prepared(
    uuid_generator, mock_regulations_repository, mock_regulations_storage, mock_session_maker
):
    user_id = next(uuid_generator)
    regulation_id = next(uuid_generator)

    regulation_rep = MagicMock()
    regulation_rep.is_prepared = True
    mock_regulations_repository.get_regulation_representation.return_value = regulation_rep

    use_case = GetRegulationUploadTarget(
        session_maker=mock_session_maker,
        regulations_repository=mock_regulations_repository,
        regulations_storage=mock_regulations_storage,
    )

    with pytest.raises(RegulationAlreadyInitialized):
        await use_case.execute(user_id, regulation_id)

    mock_regulations_storage.get_upload_target.assert_not_awaited()


# --- GetRegulationDownloadUrl Tests ---


# --- ConfirmRegulationUpload Tests ---


@pytest.mark.asyncio
async def test_confirm_regulation_upload_success(
    uuid_generator, mock_regulations_repository, mock_regulations_storage, mock_session_maker
):
    user_id = next(uuid_generator)
    regulation_id = next(uuid_generator)

    regulation_rep = MagicMock()
    regulation_rep.is_prepared = False
    mock_regulations_repository.get_regulation_representation.return_value = regulation_rep
    mock_regulations_storage.check_regulation_exists.return_value = True

    use_case = ConfirmRegulationUpload(
        session_maker=mock_session_maker,
        regulations_repository=mock_regulations_repository,
        regulations_storage=mock_regulations_storage,
    )

    await use_case.execute(user_id, regulation_id)

    mock_regulations_storage.check_regulation_exists.assert_called_once_with(regulation_id)
    mock_regulations_repository.mark_as_uploaded.assert_called_once_with(
        mock_session_maker.begin.return_value.__aenter__.return_value, user_id, regulation_id
    )


@pytest.mark.asyncio
async def test_confirm_regulation_upload_not_found(
    uuid_generator, mock_regulations_repository, mock_regulations_storage, mock_session_maker
):
    user_id = next(uuid_generator)
    regulation_id = next(uuid_generator)

    mock_regulations_repository.get_regulation_representation.return_value = None

    use_case = ConfirmRegulationUpload(
        session_maker=mock_session_maker,
        regulations_repository=mock_regulations_repository,
        regulations_storage=mock_regulations_storage,
    )

    with pytest.raises(RegulationNotFound):
        await use_case.execute(user_id, regulation_id)


@pytest.mark.asyncio
async def test_confirm_regulation_upload_already_prepared(
    uuid_generator, mock_regulations_repository, mock_regulations_storage, mock_session_maker
):
    user_id = next(uuid_generator)
    regulation_id = next(uuid_generator)

    regulation_rep = MagicMock()
    regulation_rep.is_prepared = True
    mock_regulations_repository.get_regulation_representation.return_value = regulation_rep

    use_case = ConfirmRegulationUpload(
        session_maker=mock_session_maker,
        regulations_repository=mock_regulations_repository,
        regulations_storage=mock_regulations_storage,
    )

    with pytest.raises(RegulationAlreadyInitialized):
        await use_case.execute(user_id, regulation_id)


@pytest.mark.asyncio
async def test_confirm_regulation_upload_content_not_found(
    uuid_generator, mock_regulations_repository, mock_regulations_storage, mock_session_maker
):
    user_id = next(uuid_generator)
    regulation_id = next(uuid_generator)

    regulation_rep = MagicMock()
    regulation_rep.is_prepared = False
    mock_regulations_repository.get_regulation_representation.return_value = regulation_rep
    mock_regulations_storage.check_regulation_exists.return_value = False

    use_case = ConfirmRegulationUpload(
        session_maker=mock_session_maker,
        regulations_repository=mock_regulations_repository,
        regulations_storage=mock_regulations_storage,
    )

    with pytest.raises(RegulationContentNotFound):
        await use_case.execute(user_id, regulation_id)


@pytest.mark.asyncio
async def test_get_regulation_download_url_success(
    uuid_generator, mock_regulations_repository, mock_regulations_storage, mock_session_maker
):
    user_id = next(uuid_generator)
    regulation_id = next(uuid_generator)

    mock_regulations_repository.get_regulation_representation.return_value = MagicMock()
    mock_regulations_storage.get_download_url.return_value = "http://object-storage/regulation"

    use_case = GetRegulationDownloadUrl(
        session_maker=mock_session_maker,
        regulations_repository=mock_regulations_repository,
        regulations_storage=mock_regulations_storage,
    )

    result = await use_case.execute(user_id, regulation_id)

    assert result == "http://object-storage/regulation"
    mock_regulations_storage.get_download_url.assert_awaited_once_with(regulation_id)


@pytest.mark.asyncio
async def test_get_regulation_download_url_not_found(
    uuid_generator, mock_regulations_repository, mock_regulations_storage, mock_session_maker
):
    user_id = next(uuid_generator)
    regulation_id = next(uuid_generator)

    mock_regulations_repository.get_regulation_representation.return_value = None

    use_case = GetRegulationDownloadUrl(
        session_maker=mock_session_maker,
        regulations_repository=mock_regulations_repository,
        regulations_storage=mock_regulations_storage,
    )

    with pytest.raises(RegulationNotFound):
        await use_case.execute(user_id, regulation_id)


# --- ListRegulations Tests ---


@pytest.mark.asyncio
async def test_list_regulations_success(uuid_generator, mock_regulations_repository, mock_session_maker):
    user_id = next(uuid_generator)

    mock_result = MagicMock(spec=RegulationRepresentation)
    mock_result.regulation_type = RegulationType.ACT
    mock_results = [mock_result, MagicMock(spec=RegulationRepresentation)]
    mock_regulations_repository.list_regulations.return_value = mock_results

    use_case = ListRegulations(
        session_maker=mock_session_maker,
        regulations_repository=mock_regulations_repository,
    )

    result = await use_case.execute(user_id=user_id, regulation_type=RegulationType.ACT)

    assert result == mock_results
    assert result[0].regulation_type == RegulationType.ACT
    mock_regulations_repository.list_regulations.assert_awaited_once()


# --- DeleteRegulation Tests ---


@pytest.mark.asyncio
async def test_delete_regulation_prepared_success(
    mock_session_maker,
    mock_regulations_repository,
    mock_documents_repo,
    mock_regulations_storage,
    uuid_generator,
):
    user_id = next(uuid_generator)
    regulation_id = next(uuid_generator)

    regulation_rep = MagicMock()
    regulation_rep.is_prepared = True
    mock_regulations_repository.get_regulation_representation.return_value = regulation_rep

    use_case = DeleteRegulation(
        session_maker=mock_session_maker,
        regulations_repository=mock_regulations_repository,
        documents_repository=mock_documents_repo,
        regulations_storage=mock_regulations_storage,
    )

    await use_case.execute(user_id, regulation_id)

    mock_documents_repo.remove_documents.assert_awaited_once()
    mock_regulations_repository.unregister_regulation.assert_awaited_once()
    mock_regulations_storage.delete_regulation.assert_awaited_once_with(regulation_id)


@pytest.mark.asyncio
async def test_delete_regulation_not_prepared_success(
    mock_session_maker,
    mock_regulations_repository,
    mock_documents_repo,
    mock_regulations_storage,
    uuid_generator,
):
    user_id = next(uuid_generator)
    regulation_id = next(uuid_generator)

    regulation_rep = MagicMock()
    regulation_rep.is_prepared = False
    mock_regulations_repository.get_regulation_representation.return_value = regulation_rep

    use_case = DeleteRegulation(
        session_maker=mock_session_maker,
        regulations_repository=mock_regulations_repository,
        documents_repository=mock_documents_repo,
        regulations_storage=mock_regulations_storage,
    )

    await use_case.execute(user_id, regulation_id)

    mock_documents_repo.remove_documents.assert_not_awaited()
    mock_regulations_repository.unregister_regulation.assert_awaited_once()
    mock_regulations_storage.delete_regulation.assert_awaited_once_with(regulation_id)


@pytest.mark.asyncio
async def test_delete_regulation_not_found(
    mock_session_maker,
    mock_regulations_repository,
    mock_documents_repo,
    mock_regulations_storage,
    uuid_generator,
):
    user_id = next(uuid_generator)
    regulation_id = next(uuid_generator)

    mock_regulations_repository.get_regulation_representation.return_value = None

    use_case = DeleteRegulation(
        session_maker=mock_session_maker,
        regulations_repository=mock_regulations_repository,
        documents_repository=mock_documents_repo,
        regulations_storage=mock_regulations_storage,
    )

    with pytest.raises(RegulationNotFound):
        await use_case.execute(user_id, regulation_id)


@pytest.mark.asyncio
async def test_delete_regulation_storage_error(
    mock_session_maker,
    mock_regulations_repository,
    mock_documents_repo,
    mock_regulations_storage,
    uuid_generator,
):
    user_id = next(uuid_generator)
    regulation_id = next(uuid_generator)

    regulation_rep = MagicMock()
    regulation_rep.is_prepared = True
    mock_regulations_repository.get_regulation_representation.return_value = regulation_rep

    mock_regulations_storage.delete_regulation.side_effect = Exception("Storage error")

    use_case = DeleteRegulation(
        session_maker=mock_session_maker,
        regulations_repository=mock_regulations_repository,
        documents_repository=mock_documents_repo,
        regulations_storage=mock_regulations_storage,
    )

    # Should not raise exception
    await use_case.execute(user_id, regulation_id)

    mock_documents_repo.remove_documents.assert_awaited_once()
    mock_regulations_repository.unregister_regulation.assert_awaited_once()


# --- SearchRegulation Tests ---


@pytest.mark.asyncio
async def test_search_file_success(
    mock_embedding_port,
    mock_documents_repo,
    mock_session_maker,
    uuid_generator,
    mock_opened_session,
    mock_regulations_repository,
):
    query = "test query"
    embedding_vector = [0.1, 0.2, 0.3]
    search_results = [
        {"id": "doc1", "text": "relevant document"},
        {"id": "doc2", "text": "another document"},
    ]

    user_id = next(uuid_generator)
    regulation_id = next(uuid_generator)

    mock_embedding_port.embed_queries.return_value = [embedding_vector]
    mock_documents_repo.search.return_value = search_results

    search_params = SearchParams(threshold=0, limit=None, query=query)

    use_case = SearchRegulation(
        session_maker=mock_session_maker,
        embedding_port=mock_embedding_port,
        documents_repository=mock_documents_repo,
        regulations_repository=mock_regulations_repository,
    )

    result = await use_case.execute(user_id, regulation_id, search_params)

    assert result == search_results
    mock_embedding_port.embed_queries.assert_awaited_once_with([query])
    mock_documents_repo.search.assert_awaited_once_with(
        mock_opened_session, user_id, regulation_id, embedding_vector, search_params
    )


@pytest.mark.asyncio
async def test_search_file_no_results(
    mock_embedding_port,
    mock_documents_repo,
    mock_session_maker,
    uuid_generator,
    mock_opened_session,
    mock_regulations_repository,
):
    query = "unknown query"
    embedding_vector = [0.0, 0.0, 0.0]
    search_results = []

    user_id = next(uuid_generator)
    regulation_id = next(uuid_generator)

    mock_embedding_port.embed_queries.return_value = [embedding_vector]
    mock_documents_repo.search.return_value = search_results

    search_params = SearchParams(threshold=0, limit=None, query=query)

    use_case = SearchRegulation(
        session_maker=mock_session_maker,
        embedding_port=mock_embedding_port,
        documents_repository=mock_documents_repo,
        regulations_repository=mock_regulations_repository,
    )

    result = await use_case.execute(user_id, regulation_id, search_params)

    assert result == []
    mock_embedding_port.embed_queries.assert_awaited_once_with([query])
    mock_documents_repo.search.assert_awaited_once_with(
        mock_opened_session, user_id, regulation_id, embedding_vector, search_params
    )


@pytest.mark.asyncio
async def test_search_file_embedding_error(
    mock_embedding_port, mock_session_maker, mock_documents_repo, uuid_generator, mock_regulations_repository
):
    query = "error query"
    mock_embedding_port.embed_queries.side_effect = Exception("Embedding service down")

    user_id = next(uuid_generator)
    regulation_id = next(uuid_generator)

    search_params = SearchParams(threshold=0, limit=None, query=query)

    use_case = SearchRegulation(
        session_maker=mock_session_maker,
        embedding_port=mock_embedding_port,
        documents_repository=mock_documents_repo,
        regulations_repository=mock_regulations_repository,
    )

    with pytest.raises(Exception, match="Embedding service down"):
        await use_case.execute(user_id, regulation_id, search_params)

    mock_embedding_port.embed_queries.assert_awaited_once_with([query])
    mock_documents_repo.search.assert_not_awaited()


@pytest.mark.asyncio
async def test_search_file_repository_error(
    mock_embedding_port,
    mock_documents_repo,
    mock_session_maker,
    uuid_generator,
    mock_opened_session,
    mock_regulations_repository,
):
    query = "repo error query"
    embedding_vector = [0.1, 0.1, 0.1]

    user_id = next(uuid_generator)
    regulation_id = next(uuid_generator)

    search_params = SearchParams(threshold=0, limit=None, query=query)

    mock_embedding_port.embed_queries.return_value = [embedding_vector]
    mock_documents_repo.search.side_effect = Exception("Database error")

    use_case = SearchRegulation(
        session_maker=mock_session_maker,
        embedding_port=mock_embedding_port,
        documents_repository=mock_documents_repo,
        regulations_repository=mock_regulations_repository,
    )

    with pytest.raises(Exception, match="Database error"):
        await use_case.execute(user_id, regulation_id, search_params=search_params)


@pytest.mark.asyncio
async def test_search_file_documents_not_found_but_regulation_not_found(
    mock_embedding_port,
    mock_documents_repo,
    mock_session_maker,
    uuid_generator,
    mock_regulations_repository,
):
    query = "query"
    embedding_vector = [0.1, 0.2, 0.3]
    user_id = next(uuid_generator)
    regulation_id = next(uuid_generator)

    mock_embedding_port.embed_queries.return_value = [embedding_vector]
    mock_documents_repo.search.side_effect = RegulationDocumentsNotFound
    mock_regulations_repository.get_regulation_representation.return_value = None

    search_params = SearchParams(threshold=0, limit=None, query=query)

    use_case = SearchRegulation(
        session_maker=mock_session_maker,
        embedding_port=mock_embedding_port,
        documents_repository=mock_documents_repo,
        regulations_repository=mock_regulations_repository,
    )

    with pytest.raises(RegulationNotFound):
        await use_case.execute(user_id, regulation_id, search_params)


@pytest.mark.asyncio
async def test_search_file_documents_not_found_not_prepared(
    mock_embedding_port,
    mock_documents_repo,
    mock_session_maker,
    uuid_generator,
    mock_regulations_repository,
):
    query = "query"
    embedding_vector = [0.1, 0.2, 0.3]
    user_id = next(uuid_generator)
    regulation_id = next(uuid_generator)

    mock_embedding_port.embed_queries.return_value = [embedding_vector]
    mock_documents_repo.search.side_effect = RegulationDocumentsNotFound

    regulation_rep = MagicMock()
    regulation_rep.is_prepared = False
    regulation_rep.presentation_name = "Doc"
    mock_regulations_repository.get_regulation_representation.return_value = regulation_rep

    search_params = SearchParams(threshold=0, limit=None, query=query)

    use_case = SearchRegulation(
        session_maker=mock_session_maker,
        embedding_port=mock_embedding_port,
        documents_repository=mock_documents_repo,
        regulations_repository=mock_regulations_repository,
    )

    with pytest.raises(RegulationsNotPreparedToSearch):
        await use_case.execute(user_id, regulation_id, search_params)


@pytest.mark.asyncio
async def test_search_file_documents_not_found_invalid_state(
    mock_embedding_port,
    mock_documents_repo,
    mock_session_maker,
    uuid_generator,
    mock_regulations_repository,
):
    query = "query"
    embedding_vector = [0.1, 0.2, 0.3]
    user_id = next(uuid_generator)
    regulation_id = next(uuid_generator)

    mock_embedding_port.embed_queries.return_value = [embedding_vector]
    mock_documents_repo.search.side_effect = RegulationDocumentsNotFound

    regulation_rep = MagicMock()
    regulation_rep.is_prepared = True
    mock_regulations_repository.get_regulation_representation.return_value = regulation_rep

    search_params = SearchParams(threshold=0, limit=None, query=query)

    use_case = SearchRegulation(
        session_maker=mock_session_maker,
        embedding_port=mock_embedding_port,
        documents_repository=mock_documents_repo,
        regulations_repository=mock_regulations_repository,
    )

    with pytest.raises(RegulationInInvalidState):
        await use_case.execute(user_id, regulation_id, search_params)

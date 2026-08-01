import pytest

from app.application.dtos.search import SearchParams
from app.application.use_cases.regulations import SearchRegulation


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

    mock_embedding_port.embed_queries.assert_awaited_once_with([query])
    mock_documents_repo.search.assert_awaited_once_with(
        mock_opened_session, user_id, regulation_id, embedding_vector, search_params
    )

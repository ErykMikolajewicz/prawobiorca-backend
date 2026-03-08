import pytest

from app.application.use_cases.search import SearchUserFile


@pytest.mark.asyncio
async def test_search_file_success(mock_embedding_port, mock_regulations_repo):
    query = "test query"
    embedding_vector = [0.1, 0.2, 0.3]
    search_results = [
        {"id": "doc1", "score": 0.95, "text": "relevant document"},
        {"id": "doc2", "score": 0.85, "text": "another document"},
    ]
    correct_result = ["relevant document", "another document"]

    mock_embedding_port.embed_queries.return_value = [embedding_vector]
    mock_regulations_repo.search.return_value = search_results

    file_hash_str = "abcd"

    use_case = SearchUserFile(
        embedding_port=mock_embedding_port,
        regulations_repository=mock_regulations_repo,
        query=query,
        file_hash_str=file_hash_str,
    )

    result = await use_case.execute()

    assert result == correct_result
    mock_embedding_port.embed_queries.assert_awaited_once_with([query])
    mock_regulations_repo.search.assert_awaited_once_with(
        embedding_vector, limit=5, threshold=0.0, source_file_hash="abcd"
    )


@pytest.mark.asyncio
async def test_search_file_no_results(mock_embedding_port, mock_regulations_repo):
    query = "unknown query"
    embedding_vector = [0.0, 0.0, 0.0]
    search_results = []

    mock_embedding_port.embed_queries.return_value = [embedding_vector]
    mock_regulations_repo.search.return_value = search_results

    file_hash_str = "abcd"

    use_case = SearchUserFile(
        embedding_port=mock_embedding_port,
        regulations_repository=mock_regulations_repo,
        query=query,
        file_hash_str=file_hash_str,
    )

    result = await use_case.execute()

    assert result == []
    mock_embedding_port.embed_queries.assert_awaited_once_with([query])
    mock_regulations_repo.search.assert_awaited_once_with(
        embedding_vector, limit=5, threshold=0.0, source_file_hash="abcd"
    )


@pytest.mark.asyncio
async def test_search_file_embedding_error(mock_embedding_port, mock_regulations_repo):
    query = "error query"
    mock_embedding_port.embed_queries.side_effect = Exception("Embedding service down")

    file_hash_str = "abcd"

    use_case = SearchUserFile(
        embedding_port=mock_embedding_port,
        regulations_repository=mock_regulations_repo,
        query=query,
        file_hash_str=file_hash_str,
    )

    with pytest.raises(Exception, match="Embedding service down"):
        await use_case.execute()

    mock_embedding_port.embed_queries.assert_awaited_once_with([query])
    mock_regulations_repo.search.assert_not_awaited()


@pytest.mark.asyncio
async def test_search_file_repository_error(mock_embedding_port, mock_regulations_repo):
    query = "repo error query"
    embedding_vector = [0.1, 0.1, 0.1]

    file_hash_str = "abcd"

    mock_embedding_port.embed_queries.return_value = [embedding_vector]
    mock_regulations_repo.search.side_effect = Exception("Database error")

    use_case = SearchUserFile(
        embedding_port=mock_embedding_port,
        regulations_repository=mock_regulations_repo,
        query=query,
        file_hash_str=file_hash_str,
    )

    with pytest.raises(Exception, match="Database error"):
        await use_case.execute()

    mock_embedding_port.embed_queries.assert_awaited_once_with([query])
    mock_regulations_repo.search.assert_awaited_once_with(
        embedding_vector, limit=5, threshold=0.0, source_file_hash="abcd"
    )

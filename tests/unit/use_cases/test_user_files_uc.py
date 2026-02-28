from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.application.use_cases.user_files import PrepareUserFile
from app.domain.value_objects.documents import EmbeddedDocument
from app.domain.value_objects.preparation import DocumentToEmbed


@pytest.fixture
def mock_document_embedder():
    embedder = MagicMock()
    embedder.embed_documents = AsyncMock()
    return embedder


@pytest.fixture
def mock_regulations_repo_extended(mock_regulations_repo):
    mock_regulations_repo.initialize_law_act = AsyncMock()
    mock_regulations_repo.add_documents = AsyncMock()
    return mock_regulations_repo


@pytest.fixture
def mock_user_files_repo_extended(mock_files_repo):
    mock_files_repo.get_file = AsyncMock()
    return mock_files_repo


@pytest.mark.asyncio
async def test_prepare_user_file_execute(
    mock_document_embedder, mock_user_files_repo_extended, mock_regulations_repo_extended
):
    file_name = "test_regulation.pdf"
    file_content = b"fake pdf content"

    mock_user_files_repo_extended.get_file.return_value = file_content

    mock_regulation_act = MagicMock()
    mock_doc_to_embed_1 = DocumentToEmbed(title="Ch1", text="Short text")
    mock_doc_to_embed_2 = DocumentToEmbed(title="Ch1", text="Longer text for sorting check")

    mock_regulation_act.get_documents_to_embed.return_value = [mock_doc_to_embed_2, mock_doc_to_embed_1]

    with patch("app.application.use_cases.user_files.extract_document", return_value=mock_regulation_act):
        mock_embedded_docs = [
            EmbeddedDocument(vector=[0.1, 0.2], payload={"text": "Short text"}),
            EmbeddedDocument(vector=[0.3, 0.4], payload={"text": "Longer text for sorting check"}),
        ]
        mock_document_embedder.embed_documents.return_value = mock_embedded_docs

        use_case = PrepareUserFile(
            document_embedder=mock_document_embedder,
            files_repository=mock_user_files_repo_extended,
            regulations_repository=mock_regulations_repo_extended,
            file_name=file_name,
        )

        await use_case.execute()

    mock_user_files_repo_extended.get_file.assert_awaited_once_with(file_name)

    mock_regulations_repo_extended.initialize_law_act.assert_awaited_once_with(file_name)

    mock_document_embedder.embed_documents.assert_awaited_once()
    call_args = mock_document_embedder.embed_documents.call_args[0][0]
    assert call_args[0] == mock_doc_to_embed_1
    assert call_args[1] == mock_doc_to_embed_2

    mock_regulations_repo_extended.add_documents.assert_awaited_once_with(mock_embedded_docs)

from unittest.mock import AsyncMock
from uuid import uuid4

from src.domain.value_objects.documents import Document, DocumentsCollection
from src.infrastructure.relational_db.repositories.documents import RegulationsDocumentsRepository


async def test_add_documents_saves_chunk_order():
    session = AsyncMock()
    user_id = uuid4()
    regulation_id = uuid4()

    documents = DocumentsCollection(
        [
            Document(title="Header 1", text="Content 1", chunk_order=0, vector=[0.1]),
            Document(title="Header 2", text="Content 2", chunk_order=1, vector=[0.2]),
        ]
    )

    await RegulationsDocumentsRepository.add_documents(session, user_id, regulation_id, documents)

    session.execute.assert_awaited_once()
    stmt = session.execute.await_args.args[0]
    inserted_values = stmt.compile().params

    chunk_orders = sorted(value for key, value in inserted_values.items() if key.startswith("chunk_order"))

    assert chunk_orders == [0, 1]

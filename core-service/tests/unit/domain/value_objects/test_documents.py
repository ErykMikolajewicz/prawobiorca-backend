from src.domain.value_objects.documents import Document, DocumentsCollection
from src.shared.settings.application import app_settings


def create_document(text: str) -> Document:
    return Document(title="Art. 1", text=text)


def test_documents_are_sorted_by_text_length():
    collection = DocumentsCollection([create_document("dłuższy tekst dokumentu"), create_document("krótki")])

    assert [document.text for document in collection] == ["krótki", "dłuższy tekst dokumentu"]


def test_batch_iterator_splits_documents_into_chunks():
    documents_count = app_settings.EMBED_DOCS_CHUNK_SIZE + 1
    collection = DocumentsCollection([create_document(f"tekst {index}") for index in range(documents_count)])

    batches = collection.get_batch_iterator()

    assert len(batches) == 2
    assert len(batches[0]) == app_settings.EMBED_DOCS_CHUNK_SIZE
    assert len(batches[1]) == 1

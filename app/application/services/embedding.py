from itertools import batched

from app.application.ports.embeddings import EmbeddingPort
from app.domain.value_objects.documents import DocumentPayload, EmbeddedDocument
from app.domain.value_objects.preparation import DocumentToEmbed
from app.shared.settings.application import app_settings


class DocumentEmbedder:
    def __init__(self, embedding_port):
        self._embedding_port: EmbeddingPort = embedding_port

    async def embed_documents(self, documents: list[DocumentToEmbed]) -> list[EmbeddedDocument]:
        documents.sort(key=lambda doc: len(doc.text))
        embedded_documents = []
        for chunk in batched(documents, app_settings.EMBED_DOCS_CHUNK_SIZE, strict=False):
            chunk_vectors = await self._embedding_port.embed_documents(chunk)
            for document, vector in zip(chunk, chunk_vectors, strict=True):
                payload: DocumentPayload = {"text": document.text}
                embedded_document = EmbeddedDocument(vector, payload)
                embedded_documents.append(embedded_document)
        return embedded_documents

from app.application.ports.embeddings import EmbeddingPort
from app.domain.value_objects.documents import DocumentsCollection


class DocumentEmbedder:
    def __init__(self, embedding_port):
        self._embedding_port: EmbeddingPort = embedding_port

    async def embed_documents(self, documents_collection: DocumentsCollection):
        for batch in documents_collection.get_batch_iterator():
            batch_vectors = await self._embedding_port.embed_documents(batch)
            for document, vector in zip(batch, batch_vectors, strict=True):
                document.vector = vector

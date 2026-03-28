from app.application.ports.texts import TextsEmbedder
from app.domain.value_objects.documents import DocumentsCollection


class DocumentEmbedder:
    def __init__(self, texts_embedder: TextsEmbedder):
        self._texts_embedder = texts_embedder

    async def embed_documents(self, documents_collection: DocumentsCollection):
        for batch in documents_collection.get_batch_iterator():
            batch_vectors = await self._texts_embedder.embed_documents(batch)
            for document, vector in zip(batch, batch_vectors, strict=True):
                document.vector = vector

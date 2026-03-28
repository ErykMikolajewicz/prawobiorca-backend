from app.application.ports.reguations import RegulationSpliter
from app.application.services.embedding import DocumentEmbedder
from app.domain.value_objects.documents import DocumentsCollection
from app.domain.value_objects.regulations import RegulationAct


class RegulationPreparator:
    def __init__(self, regulation_spliter: RegulationSpliter, document_embedder: DocumentEmbedder):
        self._regulation_spliter = regulation_spliter
        self._document_embedder = document_embedder

    async def prepare_regulation(self, regulation: bytes) -> DocumentsCollection:
        regulations_elements = await self._regulation_spliter.split(regulation)
        regulation_act = RegulationAct(regulations_elements)

        documents = regulation_act.get_documents_to_embed()

        await self._document_embedder.embed_documents(documents)

        return documents

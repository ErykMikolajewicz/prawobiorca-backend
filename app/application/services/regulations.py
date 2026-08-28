from app.application.ports.regulations import RegulationSplitter
from app.application.ports.tokenizer import Tokenizer
from app.application.services.embedding import DocumentEmbedder
from app.domain.value_objects.documents import DocumentsCollection
from app.domain.value_objects.regulations import RegulationAct


class RegulationPreparator:
    def __init__(
        self,
        regulation_splitter: RegulationSplitter,
        document_embedder: DocumentEmbedder,
        tokenizer: Tokenizer,
    ):
        self._regulation_splitter = regulation_splitter
        self._document_embedder = document_embedder
        self._tokenizer = tokenizer

    async def prepare_regulation(self, regulation: bytes) -> DocumentsCollection:
        regulations_elements = await self._regulation_splitter.split(regulation)
        regulation_act = RegulationAct(regulations_elements, self._tokenizer)

        documents = regulation_act.get_documents_to_embed()

        await self._document_embedder.embed_documents(documents)

        return documents

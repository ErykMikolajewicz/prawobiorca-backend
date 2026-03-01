import logging
from dataclasses import dataclass

from app.application.dtos.files import FileData
from app.application.interfaces.file_storage import UsersFilesRepository
from app.application.interfaces.regulations import RegulationsRepository
from app.application.services.embedding import DocumentEmbedder
from app.application.services.texts_extraction import extract_document
from app.domain.exceptions import FileNameExist, RegulationAlreadyInitialized

logger = logging.getLogger(__name__)


@dataclass
class PrepareUserFile:
    document_embedder: DocumentEmbedder
    files_repository: UsersFilesRepository
    regulations_repository: RegulationsRepository
    file_name: str

    async def execute(self):
        file_data = await self.files_repository.get_file(self.file_name)

        regulation_act = extract_document(file_data, self.file_name)

        try:
            await self.regulations_repository.initialize_law_act(self.file_name)
        except RegulationAlreadyInitialized:
            logger.warning("Tried prepare already prepared file!")
            raise

        documents_to_embed = regulation_act.get_documents_to_embed()
        documents_to_embed.sort(key=lambda doc: len(doc.text))

        embedded_documents = await self.document_embedder.embed_documents(documents_to_embed)
        await self.regulations_repository.add_documents(embedded_documents)


@dataclass
class AddUserFile:
    file_data: FileData
    files_repository: UsersFilesRepository

    async def execute(self):
        try:
            await self.files_repository.upload_file(self.file_data)
        except FileNameExist:
            logger.warning("File, with that name already exists!")
            raise


@dataclass
class ListUserFiles:
    files_repository: UsersFilesRepository

    async def execute(self) -> list[str]:
        files = await self.files_repository.list_files()
        return files

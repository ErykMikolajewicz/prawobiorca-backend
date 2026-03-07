import logging
from dataclasses import dataclass
from uuid import UUID

from app.application.dtos.files import FileData, FileRepresentation
from app.application.interfaces.file_managment import UserFileManager
from app.application.interfaces.file_storage import UsersFilesRepository
from app.application.interfaces.regulations import RegulationsRepository
from app.application.interfaces.relational import AsyncSession
from app.application.services.embedding import DocumentEmbedder
from app.application.services.texts_extraction import extract_document
from app.domain.exceptions import FileHashExist, RegulationAlreadyInitialized
from app.domain.services.files import hash_file
from app.domain.value_objects.user_file import UserFile

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

        embedded_documents = await self.document_embedder.embed_documents(documents_to_embed)
        await self.regulations_repository.add_documents(embedded_documents)


@dataclass
class AddUserFile:
    session: AsyncSession
    file_manager: UserFileManager
    user_id: UUID
    file_data: FileData
    files_repository: UsersFilesRepository

    async def execute(self) -> None:
        file_hash = hash_file(self.file_data.file)
        user_file = UserFile(file_hash=file_hash, user_id=self.user_id, presentation_name=self.file_data.name)

        async with self.session as session:
            try:
                await self.file_manager.register_file(user_file)
            except FileHashExist:
                logger.warning("File, with that hash is already registered!")
                raise
            try:
                await self.files_repository.upload_file(self.file_data)
            except FileExistsError:
                logger.error("File, with that hash already exists in storage!")
                raise
            await session.commit()


@dataclass
class ListUserFiles:
    session: AsyncSession
    file_manager: UserFileManager
    user_id: UUID

    async def execute(self) -> list[FileRepresentation]:
        async with self.session:
            files = await self.file_manager.list_user_files(self.user_id)
        return files

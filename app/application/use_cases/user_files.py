import base64
import logging
from dataclasses import dataclass

from app.application.dtos.files import FileData, FileRepresentation
from app.application.interfaces.file_managment import UserFileManager
from app.application.interfaces.file_storage import UsersFilesRepository
from app.application.interfaces.regulations import UserRegulationsRepository
from app.application.interfaces.relational import AsyncSession
from app.application.services.embedding import DocumentEmbedder
from app.application.services.texts_extraction import extract_document
from app.domain.exceptions import FileHashExist, RegulationAlreadyInitialized
from app.domain.services.files import hash_file
from app.domain.value_objects.documents import DocumentsCollection
from app.domain.value_objects.user_file import FileRegistrationData

logger = logging.getLogger(__name__)


@dataclass
class PrepareUserFile:
    session: AsyncSession
    document_embedder: DocumentEmbedder
    files_repository: UsersFilesRepository
    regulations_repository: UserRegulationsRepository
    file_hash_str: str
    user_file_manager: UserFileManager

    async def execute(self):
        file_hash = base64.urlsafe_b64decode(self.file_hash_str)

        async with self.session:
            try:
                file_representation = await self.user_file_manager.get_file_representation(file_hash)
            except FileNotFoundError:
                logger.warning("File to prepare not found!")
                raise

        if file_representation.is_prepared:
            logger.warning("Tried prepare already prepared file!")
            raise RegulationAlreadyInitialized

        file_content = await self.files_repository.get_file(self.file_hash_str)

        regulation_act = extract_document(file_content, file_representation.presentation_name)

        documents_to_embed = regulation_act.get_documents_to_embed()

        documents_collection = DocumentsCollection(self.file_hash_str, documents_to_embed)
        await self.document_embedder.embed_documents(documents_collection)

        await self.regulations_repository.add_documents(documents_collection)

        async with self.session as session:
            await self.user_file_manager.mark_as_prepared(file_hash)
            await session.commit()


@dataclass
class AddUserFile:
    session: AsyncSession
    file_manager: UserFileManager
    file_data: FileData
    files_repository: UsersFilesRepository

    async def execute(self) -> None:
        file_hash = hash_file(self.file_data.file)
        user_file_representation = FileRegistrationData(hash=file_hash, presentation_name=self.file_data.name)

        new_filename = base64.urlsafe_b64encode(file_hash)
        new_filename = new_filename.decode()
        self.file_data.name = new_filename

        async with self.session as session:
            try:
                await self.file_manager.register_file(user_file_representation)
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

    async def execute(self) -> list[FileRepresentation]:
        async with self.session:
            files = await self.file_manager.list_user_files()
        return files

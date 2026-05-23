import base64
import logging
from dataclasses import dataclass

from app.application.dtos.files import FileData, FileRepresentation
from app.application.interfaces.file_managment import UserFileManager
from app.application.interfaces.file_storage import UsersFilesRepository
from app.application.interfaces.regulations import UserRegulationsRepository
from app.application.interfaces.relational import AsyncSession
from app.application.services.regulations import RegulationPreparator
from app.domain.exceptions import FileHashExist, RegulationAlreadyInitialized
from app.domain.services.files import hash_file
from app.domain.value_objects.documents import DocumentType
from app.domain.value_objects.user_file import FileRegistrationData

logger = logging.getLogger(__name__)


@dataclass
class PrepareUserFile:
    session: AsyncSession
    files_repository: UsersFilesRepository
    regulations_repository: UserRegulationsRepository
    file_hash_str: str
    user_file_manager: UserFileManager
    regulation_preparator: RegulationPreparator

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

        regulation_content = await self.files_repository.get_file(self.file_hash_str)

        documents_collection = await self.regulation_preparator.prepare_regulation(regulation_content)

        await self.regulations_repository.add_documents(self.file_hash_str, documents_collection)

        async with self.session as session:
            await self.user_file_manager.mark_as_prepared(file_hash)
            await session.commit()


@dataclass
class AddUserFile:
    session: AsyncSession
    file_manager: UserFileManager
    file_data: FileData
    files_repository: UsersFilesRepository
    document_type: DocumentType | None

    async def execute(self) -> FileRepresentation:
        file_hash = hash_file(self.file_data.file)
        user_file_representation = FileRegistrationData(
            hash=file_hash, presentation_name=self.file_data.name, document_type=self.document_type
        )

        new_filename = base64.urlsafe_b64encode(file_hash)
        new_filename = new_filename.decode()
        self.file_data.name = new_filename
        self.file_data.document_type = self.document_type

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

        file_representation = FileRepresentation(
            file_hash_str=new_filename, presentation_name=self.file_data.name, is_prepared=False
        )

        return file_representation


@dataclass
class ListUserFiles:
    session: AsyncSession
    file_manager: UserFileManager
    document_type: DocumentType | None

    async def execute(self) -> list[FileRepresentation]:
        async with self.session:
            files = await self.file_manager.list_user_files(self.document_type)
        return files


@dataclass
class DeleteUserFile:
    session: AsyncSession
    file_manager: UserFileManager
    regulations_repository: UserRegulationsRepository
    file_hash_str: str
    files_repository: UsersFilesRepository

    async def execute(self):
        file_hash = base64.urlsafe_b64decode(self.file_hash_str)

        async with self.session:
            try:
                file_representation = await self.file_manager.get_file_representation(file_hash)
            except FileNotFoundError:
                logger.warning(f"User file to delete not found! File hash: {self.file_hash_str}")
                raise

        if file_representation.is_prepared:
            await self.regulations_repository.remove_documents(self.file_hash_str)

        async with self.session as session:
            await self.file_manager.unregister_file(file_hash)
            await self.files_repository.delete_file(self.file_hash_str)
            await session.commit()

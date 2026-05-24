import logging
from dataclasses import dataclass
from uuid import UUID

from app.application.dtos.regulations import RegulationData, RegulationRepresentation
from app.application.dtos.search import SearchParams, SearchResult
from app.application.interfaces.documents import DocumentsRepository
from app.application.interfaces.regulations import RegulationsManager, RegulationsRepository
from app.application.interfaces.relational import AsyncSession
from app.application.ports.texts import TextsEmbedder
from app.application.services.regulations import RegulationPreparator
from app.domain.exceptions import RegulationAlreadyInitialized
from app.domain.value_objects.regulations import RegulationType, RegulationRegistrationData

logger = logging.getLogger(__name__)


@dataclass
class PrepareRegulation:
    session: AsyncSession
    regulations_repository: RegulationsRepository
    documents_repository: DocumentsRepository
    regulation_id: UUID
    regulations_manager: RegulationsManager
    regulation_preparator: RegulationPreparator

    async def execute(self):
        async with self.session:
            try:
                file_representation = await self.regulations_manager.get_regulation_representation(self.regulation_id)
            except FileNotFoundError:
                logger.warning("File to prepare not found!")
                raise

        if file_representation.is_prepared:
            logger.warning("Tried prepare already prepared file!")
            raise RegulationAlreadyInitialized

        regulation_content = await self.regulations_repository.get_regulation(self.regulation_id)

        documents_collection = await self.regulation_preparator.prepare_regulation(regulation_content)

        async with self.session as session:
            await self.documents_repository.add_documents(self.regulation_id, documents_collection)
            await self.regulations_manager.mark_as_prepared(self.regulation_id)
            await session.commit()


@dataclass
class AddRegulation:
    session: AsyncSession
    regulation_manager: RegulationsManager
    regulation_data: RegulationData
    regulation_repository: RegulationsRepository
    regulation_type: RegulationType | None

    async def execute(self) -> RegulationRepresentation:
        regulation_registration_data = RegulationRegistrationData(presentation_name=self.regulation_data.name,
                                                                  document_type=self.regulation_type
                                                                  )
        async with self.session as session:
            regulation_id = await self.regulation_manager.register_regulation(regulation_registration_data)

            try:
                await self.regulation_repository.upload_regulation(regulation_id, self.regulation_data.file)
            except FileExistsError:
                logger.error("File, with that hash already exists in storage!")
                raise
            await session.commit()

        file_representation = RegulationRepresentation(
            id=regulation_id, presentationName=self.regulation_data.name, isPrepared=False
        )

        return file_representation


@dataclass
class ListRegulations:
    session: AsyncSession
    regulations_manager: RegulationsManager
    regulation_type: RegulationType | None

    async def execute(self) -> list[RegulationRepresentation]:
        async with self.session:
            files = await self.regulations_manager.list_regulations(self.regulation_type)
        return files


@dataclass
class DeleteRegulation:
    session: AsyncSession
    regulations_manager: RegulationsManager
    documents_repository: DocumentsRepository
    regulation_id: UUID
    regulations_repository: RegulationsRepository

    async def execute(self):
        async with self.session:
            try:
                regulation_representation = await self.regulations_manager.get_regulation_representation(
                    self.regulation_id)
            except FileNotFoundError:
                logger.warning(f"User file to delete not found! File hash: {self.regulation_id}")
                raise

        if regulation_representation.is_prepared:
            await self.documents_repository.remove_documents(self.regulation_id)

        async with self.session as session:
            await self.regulations_manager.unregister_regulation(self.regulation_id)
            await self.regulations_repository.delete_regulation(self.regulation_id)
            await session.commit()


@dataclass
class SearchRegulation:
    embedding_port: TextsEmbedder
    documents_repository: DocumentsRepository
    query: str
    search_params: SearchParams

    async def execute(self) -> list[SearchResult]:
        embeddings = await self.embedding_port.embed_queries([self.query])
        query_vector = embeddings[0]
        results = await self.documents_repository.search(query_vector, self.search_params)
        return results

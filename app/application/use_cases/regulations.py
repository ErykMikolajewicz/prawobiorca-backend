import logging
from dataclasses import dataclass
from uuid import UUID

from app.application.dtos.regulations import RegulationData, RegulationRepresentation
from app.application.dtos.search import SearchParams, SearchResult
from app.application.interfaces.documents import DocumentsRepository
from app.application.interfaces.regulations import RegulationsManager, RegulationsRepository
from app.application.interfaces.relational import SessionMaker
from app.application.ports.texts import TextsEmbedder
from app.application.services.regulations import RegulationPreparator
from app.domain.exceptions import RegulationAlreadyInitialized
from app.domain.value_objects.regulations import RegulationRegistrationData, RegulationType

logger = logging.getLogger(__name__)


@dataclass
class PrepareRegulation:
    session_maker: SessionMaker
    regulations_repository: RegulationsRepository
    documents_repository: DocumentsRepository
    regulations_manager: RegulationsManager
    regulation_preparator: RegulationPreparator

    async def execute(self, user_id: UUID | None, regulation_id: UUID):
        async with self.session_maker() as session:
            try:
                file_representation = await self.regulations_manager.get_regulation_representation(
                    session, user_id, regulation_id
                )
            except FileNotFoundError:
                logger.warning("regulation to prepare not found!")
                raise

        if file_representation.is_prepared:
            logger.warning("Tried prepare already prepared regulation!")
            raise RegulationAlreadyInitialized

        regulation_content = await self.regulations_repository.get_regulation(regulation_id)

        documents_collection = await self.regulation_preparator.prepare_regulation(regulation_content)

        async with self.session_maker.begin() as session:
            await self.documents_repository.add_documents(session, regulation_id, documents_collection)
            await self.regulations_manager.mark_as_prepared(session, user_id, regulation_id)


@dataclass
class AddRegulation:
    session_maker: SessionMaker
    regulation_manager: RegulationsManager
    regulation_repository: RegulationsRepository

    async def execute(
        self, user_id: UUID | None, regulation_type: RegulationType | None, regulation_data: RegulationData
    ) -> UUID:
        regulation_registration_data = RegulationRegistrationData(
            presentation_name=regulation_data.name, document_type=regulation_type
        )
        async with self.session_maker.begin() as session:
            regulation_id = await self.regulation_manager.register_regulation(
                session, user_id, regulation_registration_data
            )
            try:
                await self.regulation_repository.upload_regulation(regulation_id, regulation_data.file)
            except FileExistsError:
                logger.error("File, with that hash already exists in storage!")
                raise

        return regulation_id


@dataclass
class ListRegulations:
    session_maker: SessionMaker
    regulations_manager: RegulationsManager

    async def execute(
        self, user_id: UUID | None, regulation_type: RegulationType | None
    ) -> list[RegulationRepresentation]:
        async with self.session_maker() as session:
            files = await self.regulations_manager.list_regulations(session, user_id, regulation_type)
        return files


@dataclass
class DeleteRegulation:
    session_maker: SessionMaker
    regulations_manager: RegulationsManager
    documents_repository: DocumentsRepository
    regulations_repository: RegulationsRepository

    async def execute(self, user_id: UUID | None, regulation_id: UUID):
        async with self.session_maker() as session:
            try:
                regulation_representation = await self.regulations_manager.get_regulation_representation(
                    session, user_id, regulation_id
                )
            except FileNotFoundError:
                logger.warning(f"User regulation not found! regulation id: {regulation_id}")
                raise

            if regulation_representation.is_prepared:
                await self.documents_repository.remove_documents(session, regulation_id)

        async with self.session_maker.begin() as session:
            await self.regulations_manager.unregister_regulation(session, user_id, regulation_id)
            await self.regulations_repository.delete_regulation(regulation_id)


@dataclass
class SearchRegulation:
    session_maker: SessionMaker
    embedding_port: TextsEmbedder
    documents_repository: DocumentsRepository

    async def execute(self, user_id: UUID | None, regulation_id, search_params: SearchParams) -> list[SearchResult]:
        embeddings = await self.embedding_port.embed_queries([search_params.query])
        query_vector = embeddings[0]

        async with self.session_maker() as session:
            results = await self.documents_repository.search(
                session, user_id, regulation_id, query_vector, search_params
            )
        return results

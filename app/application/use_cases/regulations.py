import logging
from dataclasses import dataclass
from uuid import UUID

from app.application.dtos.regulations import RegulationData, RegulationRepresentation, RegulationUploadTarget
from app.application.dtos.search import SearchParams, SearchResult
from app.application.interfaces.documents import DocumentsRepository
from app.application.interfaces.regulations import RegulationsRepository, RegulationsStorage
from app.application.interfaces.relational import SessionMaker
from app.application.ports.texts import TextsEmbedder
from app.application.services.regulations import RegulationPreparator
from app.domain.exceptions.documents import RegulationDocumentsNotFound
from app.domain.exceptions.regulations import (
    RegulationAlreadyInitialized,
    RegulationContentNotFound,
    RegulationInInvalidState,
    RegulationNotFound,
    RegulationServiceUnavailable,
    RegulationsNotPreparedToSearch,
)
from app.domain.value_objects.regulations import RegulationRegistrationData, RegulationType

logger = logging.getLogger(__name__)


@dataclass
class PrepareRegulation:
    session_maker: SessionMaker
    regulations_storage: RegulationsStorage
    documents_repository: DocumentsRepository
    regulations_repository: RegulationsRepository
    regulation_preparator: RegulationPreparator

    async def execute(self, user_id: UUID | None, regulation_id: UUID):
        async with self.session_maker() as session:
            file_representation = await self.regulations_repository.get_regulation_representation(
                session, user_id, regulation_id
            )
            if file_representation is None:
                logger.warning("Regulation to prepare not found!")
                raise RegulationNotFound

        if file_representation.is_prepared:
            logger.warning("Tried prepare already prepared regulation!")
            raise RegulationAlreadyInitialized

        try:
            regulation_content = await self.regulations_storage.get_regulation(regulation_id)
        except RegulationContentNotFound:
            logger.error(f"Regulation content not found! regulation id: {regulation_id}")
            raise

        try:
            documents_collection = await self.regulation_preparator.prepare_regulation(regulation_content)
        except Exception as e:
            logger.error(f"Service to prepare regulation not working! {str(e)}")
            raise RegulationServiceUnavailable()

        async with self.session_maker.begin() as session:
            await self.documents_repository.add_documents(session, user_id, regulation_id, documents_collection)
            await self.regulations_repository.mark_as_prepared(session, user_id, regulation_id)


@dataclass
class AddRegulation:
    session_maker: SessionMaker
    regulations_repository: RegulationsRepository

    async def execute(self, user_id: UUID | None, regulation_data: RegulationData) -> UUID:
        regulation_registration_data = RegulationRegistrationData(
            presentation_name=regulation_data.name, regulation_type=regulation_data.regulation_type
        )
        async with self.session_maker.begin() as session:
            regulation_id = await self.regulations_repository.register_regulation(
                session, user_id, regulation_registration_data
            )

        return regulation_id


@dataclass
class GetRegulationUploadTarget:
    session_maker: SessionMaker
    regulations_repository: RegulationsRepository
    regulations_storage: RegulationsStorage

    async def execute(self, user_id: UUID | None, regulation_id: UUID) -> RegulationUploadTarget:
        async with self.session_maker() as session:
            regulation_representation = await self.regulations_repository.get_regulation_representation(
                session, user_id, regulation_id
            )

        if regulation_representation is None:
            logger.warning(f"Regulation to upload not found! regulation id: {regulation_id}")
            raise RegulationNotFound

        if regulation_representation.is_prepared:
            logger.warning(f"Tried upload content of prepared regulation! regulation id: {regulation_id}")
            raise RegulationAlreadyInitialized

        return await self.regulations_storage.get_upload_target(regulation_id)


@dataclass
class ConfirmRegulationUpload:
    session_maker: SessionMaker
    regulations_repository: RegulationsRepository
    regulations_storage: RegulationsStorage

    async def execute(self, user_id: UUID | None, regulation_id: UUID) -> None:
        async with self.session_maker.begin() as session:
            regulation_representation = await self.regulations_repository.get_regulation_representation(
                session, user_id, regulation_id
            )

            if regulation_representation is None:
                logger.warning(f"Regulation to confirm upload not found! regulation id: {regulation_id}")
                raise RegulationNotFound

            if regulation_representation.is_prepared:
                logger.warning(
                    f"Tried to confirm upload for already prepared regulation! regulation id: {regulation_id}"
                )
                raise RegulationAlreadyInitialized

            is_in_storage = await self.regulations_storage.check_regulation_exists(regulation_id)
            if not is_in_storage:
                logger.error(
                    f"Cannot confirm upload: Regulation content not found in storage! regulation id: {regulation_id}"
                )
                raise RegulationContentNotFound

            await self.regulations_repository.mark_as_uploaded(session, user_id, regulation_id)

        return await self.regulations_storage.get_upload_target(regulation_id)


@dataclass
class GetRegulationDownloadUrl:
    session_maker: SessionMaker
    regulations_repository: RegulationsRepository
    regulations_storage: RegulationsStorage

    async def execute(self, user_id: UUID | None, regulation_id: UUID) -> str:
        async with self.session_maker() as session:
            regulation_representation = await self.regulations_repository.get_regulation_representation(
                session, user_id, regulation_id
            )

        if regulation_representation is None:
            logger.warning(f"Regulation to download not found! regulation id: {regulation_id}")
            raise RegulationNotFound

        return await self.regulations_storage.get_download_url(regulation_id)


@dataclass
class ListRegulations:
    session_maker: SessionMaker
    regulations_repository: RegulationsRepository

    async def execute(
        self, user_id: UUID | None, regulation_type: RegulationType | None
    ) -> list[RegulationRepresentation]:
        async with self.session_maker() as session:
            files = await self.regulations_repository.list_regulations(session, user_id, regulation_type)
        return files


@dataclass
class DeleteRegulation:
    session_maker: SessionMaker
    regulations_repository: RegulationsRepository
    documents_repository: DocumentsRepository
    regulations_storage: RegulationsStorage

    async def execute(self, user_id: UUID | None, regulation_id: UUID):
        async with self.session_maker.begin() as session:
            regulation_representation = await self.regulations_repository.get_regulation_representation(
                session, user_id, regulation_id
            )
            if regulation_representation is None:
                logger.warning(f"Regulation not found! regulation id: {regulation_id}")
                raise RegulationNotFound

            if regulation_representation.is_prepared:
                await self.documents_repository.remove_documents(session, user_id, regulation_id)
            await self.regulations_repository.unregister_regulation(session, user_id, regulation_id)

        try:
            # Orphaned files are tolerable, too much hassle with eventual consistency
            await self.regulations_storage.delete_regulation(regulation_id)
        except Exception:
            logger.error(f"Failed to remove from storage regulation: {regulation_id}")


@dataclass
class SearchRegulation:
    session_maker: SessionMaker
    embedding_port: TextsEmbedder
    documents_repository: DocumentsRepository
    regulations_repository: RegulationsRepository

    async def execute(self, user_id: UUID | None, regulation_id, search_params: SearchParams) -> list[SearchResult]:

        embeddings = await self.embedding_port.embed_queries([search_params.query])
        query_vector = embeddings[0]

        async with self.session_maker() as session:
            try:
                results = await self.documents_repository.search(
                    session, user_id, regulation_id, query_vector, search_params
                )
            except RegulationDocumentsNotFound:
                logger.warning(f"Regulation to search has no prepared documents! regulation id: {regulation_id}")

                regulation_representation = await self.regulations_repository.get_regulation_representation(
                    session, user_id, regulation_id
                )

                if regulation_representation is None:
                    logger.warning(f"Regulation not found! regulation id: {regulation_id}")
                    raise RegulationNotFound

                if not regulation_representation.is_prepared:
                    logger.warning(f"Regulation to search not prepared! regulation id: {regulation_id}")
                    raise RegulationsNotPreparedToSearch(regulations_name=regulation_representation.presentation_name)

                logger.error("Regulation prepared, but documents not found!")
                raise RegulationInInvalidState
        return results

from uuid import UUID

from sqlalchemy import delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dtos.search import SearchParams, SearchResult
from app.domain.exceptions.documents import RegulationDocumentsNotFound
from app.domain.value_objects.documents import DocumentsCollection
from app.infrastructure.relational_db.schemas.documents import regulations_documents_table


class RegulationsDocumentsRepository:
    @staticmethod
    async def add_documents(
        session: AsyncSession,
        user_id: UUID | None,
        regulation_id: UUID,
        documents: DocumentsCollection,
    ) -> None:
        articles_data = [
            {
                "id": document.id,
                "header": document.title,
                "text": document.text,
                "chunk_order": document.chunk_order,
                "vector": document.vector,
                "regulation_id": regulation_id,
                "user_id": user_id,
            }
            for document in documents
        ]

        stmt = insert(regulations_documents_table).values(articles_data)
        await session.execute(stmt)

    @staticmethod
    async def search(
        session: AsyncSession,
        user_id: UUID | None,
        regulation_id: UUID,
        vector: list[float],
        search_params: SearchParams,
    ) -> list[SearchResult]:
        exists_query = (
            select(1)
            .where(
                regulations_documents_table.c.regulation_id == regulation_id,
                regulations_documents_table.c.user_id == user_id,
            )
            .limit(1)
        )
        exists_result = await session.execute(exists_query)
        if not exists_result.scalar():
            raise RegulationDocumentsNotFound()

        limit = search_params.limit
        if limit is None:
            limit = 2**32

        distance = regulations_documents_table.c.vector.cosine_distance(vector)

        subquery = (
            select(
                regulations_documents_table.c.id,
                regulations_documents_table.c.header,
                regulations_documents_table.c.text,
                regulations_documents_table.c.chunk_order,
                distance.label("distance"),
            )
            .where(
                regulations_documents_table.c.regulation_id == regulation_id,
                regulations_documents_table.c.user_id == user_id,
            )
            .order_by(distance.asc())
            .limit(limit)
        )

        if search_params.threshold is not None:
            subquery = subquery.where(distance <= 1 - search_params.threshold)

        subquery = subquery.subquery()

        query = select(subquery).order_by(subquery.c.chunk_order.asc())

        result = await session.execute(query)
        rows = result.all()

        return [
            SearchResult(
                id=row.id,
                header=row.header,
                text=row.text,
                score=1 - row.distance,
            )
            for row in rows
        ]

    @staticmethod
    async def remove_documents(session: AsyncSession, user_id, regulation_id: UUID) -> None:
        query = delete(regulations_documents_table).where(
            regulations_documents_table.c.regulation_id == regulation_id,
            regulations_documents_table.c.user_id == user_id,
        )

        await session.execute(query)

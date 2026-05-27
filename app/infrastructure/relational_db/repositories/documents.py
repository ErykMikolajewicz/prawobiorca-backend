from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dtos.search import SearchParams, SearchResult
from app.domain.value_objects.documents import DocumentsCollection
from app.infrastructure.relational_db.schemas.documents import RegulationsDocuments


class RegulationsDocumentsRepository:
    def __init__(self):
        self._model = RegulationsDocuments

    async def add_documents(
        self,
        session: AsyncSession,
        user_id: UUID | None,
        regulation_id: UUID,
        documents: DocumentsCollection,
    ) -> None:
        articles = [
            self._model(
                id=document.id,
                header=getattr(document, "header", None),
                text=document.text,
                vector=document.vector,
                regulation_id=regulation_id,
                user_id=user_id,
            )
            for document in documents
        ]

        session.add_all(articles)
        await session.flush()

    async def search(
        self,
        session: AsyncSession,
        user_id: UUID | None,
        regulation_id: UUID,
        vector: list[float],
        search_params: SearchParams,
    ) -> list[SearchResult]:
        limit = search_params.limit
        if limit is None:
            limit = 2**32

        distance = self._model.vector.cosine_distance(vector)

        query = (
            select(
                self._model.id,
                self._model.text,
                distance.label("distance"),
            )
            .where(self._model.regulation_id == regulation_id, self._model.user_id == user_id)
            .order_by(distance.asc())
            .limit(limit)
        )

        if search_params.threshold is not None:
            query = query.where(distance <= 1 - search_params.threshold)

        result = await session.execute(query)
        rows = result.all()

        return [
            SearchResult(
                id=row.id,
                text=row.text,
                score=1 - row.distance,
            )
            for row in rows
        ]

    async def remove_documents(self, session: AsyncSession, user_id, regulation_id: UUID) -> None:
        query = delete(self._model).where(self._model.regulation_id == regulation_id, self._model.user_id == user_id)

        await session.execute(query)
        await session.flush()

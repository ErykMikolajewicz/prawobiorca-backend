from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dtos.search import SearchParams, SearchResult
from app.domain.value_objects.documents import DocumentsCollection
from app.infrastructure.relational_db.schemas.regulations import RegulationsArticles


class PostgresRegulationsRepository:
    def __init__(
        self,
        session: AsyncSession,
        user_id: UUID | None = None,
    ):
        self._session = session
        self._user_id = user_id

    async def add_documents(
        self,
        source_file_hash: str,
        documents: DocumentsCollection,
    ) -> None:
        articles = [
            RegulationsArticles(
                id=document.id,
                header=getattr(document, "header", None),
                text=document.text,
                vector=document.vector,
                user_id=self._user_id,
                source_file_hash=source_file_hash,
            )
            for document in documents
        ]

        self._session.add_all(articles)
        await self._session.flush()

    async def search(
        self,
        vector: list[float],
        search_params: SearchParams,
    ) -> list[SearchResult]:
        limit = search_params.limit
        if limit is None:
            limit = 2**32

        distance = RegulationsArticles.vector.cosine_distance(vector)

        query = (
            select(
                RegulationsArticles.id,
                RegulationsArticles.text,
                distance.label("distance"),
            )
            .where(
                RegulationsArticles.regulation_id == search_params.regulation_id,
                self._user_filter(),
            )
            .order_by(distance.asc())
            .limit(limit)
        )

        if search_params.threshold is not None:
            query = query.where(distance <= 1 - search_params.threshold)

        result = await self._session.execute(query)
        rows = result.all()

        return [
            SearchResult(
                id=row.id,
                text=row.text,
                score=1 - row.distance,
            )
            for row in rows
        ]

    async def remove_documents(self, regulation_id: UUID
    ) -> None:
        query = delete(RegulationsArticles).where(
            RegulationsArticles.regulation_id == regulation_id,
            self._user_filter(),
        )

        await self._session.execute(query)
        await self._session.flush()

    def _user_filter(self):
        if self._user_id is None:
            return RegulationsArticles.user_id.is_(None)

        return RegulationsArticles.user_id == self._user_id
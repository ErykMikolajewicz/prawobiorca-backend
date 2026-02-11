from dataclasses import dataclass

from app.domain.interfaces.vector_db import VectorDBRepository
from app.domain.ports.embeddings import EmbeddingPort


@dataclass
class SearchFile:
    embedding_port: EmbeddingPort
    vector_db_repository: VectorDBRepository
    query: str

    async def execute(self) -> list[dict]:
        embeddings = await self.embedding_port.embed_queries([self.query])
        query_vector = embeddings[0]
        results = await self.vector_db_repository.search(query_vector, limit=5, threshold=0.0)
        return results

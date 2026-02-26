from dataclasses import dataclass

from app.application.interfaces.regulations import RegulationsRepository
from app.application.ports.embeddings import EmbeddingPort


@dataclass
class SearchFile:
    embedding_port: EmbeddingPort
    regulations_repository: RegulationsRepository
    query: str

    async def execute(self) -> list[dict]:
        embeddings = await self.embedding_port.embed_queries([self.query])
        query_vector = embeddings[0]
        results = await self.regulations_repository.search(query_vector, limit=5, threshold=0.0)
        results = [result["text"] for result in results]
        return results

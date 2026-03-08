from dataclasses import dataclass

from app.application.interfaces.regulations import PublicRegulationsRepository, UserRegulationsRepository
from app.application.ports.embeddings import EmbeddingPort


@dataclass
class SearchUserFile:
    embedding_port: EmbeddingPort
    regulations_repository: UserRegulationsRepository
    query: str
    file_hash_str: str

    async def execute(self) -> list[str]:
        embeddings = await self.embedding_port.embed_queries([self.query])
        query_vector = embeddings[0]
        results = await self.regulations_repository.search(
            query_vector, limit=10, threshold=0.5, source_file_hash=self.file_hash_str
        )
        results = [result["text"] for result in results]
        return results


@dataclass
class SearchPublicFile:
    embedding_port: EmbeddingPort
    regulations_repository: PublicRegulationsRepository
    query: str
    file_hash_str: str

    async def execute(self) -> list[str]:
        embeddings = await self.embedding_port.embed_queries([self.query])
        query_vector = embeddings[0]
        results = await self.regulations_repository.search(
            query_vector, limit=5, threshold=0.0, source_file_hash=self.file_hash_str
        )
        results = [result["text"] for result in results]
        return results

from dataclasses import dataclass

from app.application.dtos.search import SearchResult
from app.application.interfaces.regulations import PublicRegulationsRepository, UserRegulationsRepository
from app.application.ports.texts import TextsEmbedder


@dataclass
class SearchUserFile:
    embedding_port: TextsEmbedder
    regulations_repository: UserRegulationsRepository
    query: str
    file_hash_str: str

    async def execute(self) -> list[SearchResult]:
        embeddings = await self.embedding_port.embed_queries([self.query])
        query_vector = embeddings[0]
        results = await self.regulations_repository.search(
            query_vector, limit=10, threshold=0.5, source_file_hash=self.file_hash_str
        )
        return results


@dataclass
class SearchPublicFile:
    embedding_port: TextsEmbedder
    regulations_repository: PublicRegulationsRepository
    query: str
    file_hash_str: str

    async def execute(self) -> list[SearchResult]:
        embeddings = await self.embedding_port.embed_queries([self.query])
        query_vector = embeddings[0]
        results = await self.regulations_repository.search(
            query_vector, limit=5, threshold=0.0, source_file_hash=self.file_hash_str
        )
        return results

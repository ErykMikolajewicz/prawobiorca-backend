from dataclasses import dataclass

from app.application.dtos.search import SearchParams, SearchResult
from app.application.interfaces.regulations import PublicRegulationsRepository, UserRegulationsRepository
from app.application.ports.texts import TextsEmbedder


@dataclass
class SearchUserFile:
    embedding_port: TextsEmbedder
    regulations_repository: UserRegulationsRepository
    query: str
    search_params: SearchParams

    async def execute(self) -> list[SearchResult]:
        embeddings = await self.embedding_port.embed_queries([self.query])
        query_vector = embeddings[0]
        results = await self.regulations_repository.search(query_vector, self.search_params)
        return results


@dataclass
class SearchPublicFile:
    embedding_port: TextsEmbedder
    regulations_repository: PublicRegulationsRepository
    query: str
    search_params: SearchParams

    async def execute(self) -> list[SearchResult]:
        embeddings = await self.embedding_port.embed_queries([self.query])
        query_vector = embeddings[0]
        results = await self.regulations_repository.search(query_vector, self.search_params)
        return results

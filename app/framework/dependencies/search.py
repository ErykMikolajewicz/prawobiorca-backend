from typing import Annotated

from fastapi import Depends, Form

from app.application.use_cases.search import SearchFile
from app.framework.dependencies.embeddings import get_embeddings_port
from app.framework.dependencies.regulations import get_regulations_repository
from app.domain.ports.embeddings import EmbeddingPort
from app.domain.interfaces.vector_db import RegulationsRepository


def get_search_file(query: Annotated[str, Form()],
                    embedding_port: Annotated[EmbeddingPort, Depends(get_embeddings_port)],
                    regulations_repository: Annotated[RegulationsRepository,
                    Depends(get_regulations_repository)]) -> SearchFile:
    return SearchFile(embedding_port, regulations_repository, query)

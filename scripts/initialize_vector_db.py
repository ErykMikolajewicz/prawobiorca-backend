import asyncio
import base64
import sys
from hashlib import sha256
from pathlib import Path

sys.path.append(".")

import httpx
from app.application.services.texts_extraction import extract_document
from app.infrastructure.embeddings.httpx_client.port import HttpxEmbeddingsPort
from app.shared.settings.embeddings import embeddings_settings
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from app.infrastructure.relational_db.connection import async_session_maker
from app.infrastructure.relational_db.schemas.files import PublicFiles
from app.shared.consts import VECTOR_DB_PUBLIC_COLLECTION_NAME, VECTOR_DB_USERS_COLLECTION_NAME
from app.shared.settings.qdrant_database import qdrant_settings

qdrant_client: AsyncQdrantClient = AsyncQdrantClient(
    host=qdrant_settings.HOST, grpc_port=qdrant_settings.GRPC_PORT, prefer_grpc=True, https=False
)


async def initialize_vector_db():
    vectors_config = VectorParams(size=768, distance=Distance.COSINE)

    await qdrant_client.create_collection(VECTOR_DB_USERS_COLLECTION_NAME, vectors_config)
    await qdrant_client.create_collection(VECTOR_DB_PUBLIC_COLLECTION_NAME, vectors_config)


async def fulfill_public_collection():
    init_files_dir = Path("scripts/init_files")
    for file_path in init_files_dir.iterdir():
        file_name = file_path.name
        with open(file_path, "rb") as file:
            file_content = file.read()

        file_hash = sha256(file_content).digest()
        file_hash_str = base64.urlsafe_b64encode(file_hash).decode()

        regulation = extract_document(file_content, file_name)
        documents_to_embed = regulation.get_documents_to_embed()

        async with httpx.AsyncClient(timeout=300) as client:
            embeddings_port = HttpxEmbeddingsPort(client=client, embedding_url=embeddings_settings.URL)
            vectors = await embeddings_port.embed_documents(documents_to_embed)

        points = []
        for vector, document in zip(vectors, documents_to_embed, strict=True):
            payload = {
                "text": document.text,
                "source_file_hash": file_hash_str,
            }
            point = PointStruct(
                id=str(document.id),
                vector=vector,
                payload=payload,
            )
            points.append(point)

        async with async_session_maker() as session:
            public_file = PublicFiles(hash=file_hash, presentation_name=file_name, is_prepared=True)
            session.add(public_file)

            file_destination = Path("files/public") / file_hash_str
            with open(file_destination, "wb") as file:
                file.write(file_content)

            await qdrant_client.upsert(collection_name=VECTOR_DB_PUBLIC_COLLECTION_NAME, points=points)

            await session.commit()


async def main():
    await initialize_vector_db()
    await fulfill_public_collection()


if __name__ == "__main__":
    asyncio.run(main())

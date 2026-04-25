import asyncio
import base64
import sys
from hashlib import sha256
from pathlib import Path

sys.path.append("")

import grpc
import httpx
from grpc.aio import AioRpcError
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from app.application.services.embedding import DocumentEmbedder
from app.application.services.regulations import RegulationPreparator
from app.infrastructure.relational_db.connection import async_session_maker
from app.infrastructure.relational_db.schemas.files import PublicFiles
from app.infrastructure.text_transformator.regulation_splitter import RegulationSplitter
from app.infrastructure.text_transformator.text_embedder import TextsEmbedder
from app.shared.consts import VECTOR_DB_PUBLIC_COLLECTION_NAME, VECTOR_DB_USERS_COLLECTION_NAME
from app.shared.settings.qdrant_database import qdrant_settings
from app.shared.settings.text_transformator import text_transformator_settings

qdrant_client: AsyncQdrantClient = AsyncQdrantClient(
    host=qdrant_settings.HOST, grpc_port=qdrant_settings.GRPC_PORT, prefer_grpc=True, https=False
)


async def initialize_vector_db():
    vectors_config = VectorParams(size=768, distance=Distance.COSINE)
    try:
        await qdrant_client.create_collection(VECTOR_DB_USERS_COLLECTION_NAME, vectors_config)
    except AioRpcError as e:
        if e.code() == grpc.StatusCode.ALREADY_EXISTS:
            pass
        else:
            raise

    try:
        await qdrant_client.create_collection(VECTOR_DB_PUBLIC_COLLECTION_NAME, vectors_config)
    except AioRpcError as e:
        if e.code() == grpc.StatusCode.ALREADY_EXISTS:
            pass
        else:
            raise


async def fulfill_public_collection():
    init_files_dir = Path("scripts/init_files")
    for file_path in init_files_dir.iterdir():
        file_name = file_path.name
        with open(file_path, "rb") as file:
            file_content = file.read()

        file_hash = sha256(file_content).digest()
        file_hash_str = base64.urlsafe_b64encode(file_hash).decode()

        async with httpx.AsyncClient(timeout=900) as client:
            texts_embedder = TextsEmbedder(client=client, texts_transformator_url=text_transformator_settings.URL)
            regulation_spliter = RegulationSplitter(
                client=client, texts_transformator_url=text_transformator_settings.URL
            )
            document_embedder = DocumentEmbedder(texts_embedder)
            regulation_preparator = RegulationPreparator(regulation_spliter, document_embedder)
            documents_to_embed = await regulation_preparator.prepare_regulation(file_content)
            print(f"Embedded regulation: {file_name}")
        documents_batch_iterator = documents_to_embed.get_batch_iterator()
        points = []
        for documents_batch in documents_batch_iterator:
            for document in documents_batch:
                payload = {
                    "text": document.text,
                    "source_file_hash": file_hash_str,
                }
                point = PointStruct(
                    id=str(document.id),
                    vector=document.vector,
                    payload=payload,
                )
                points.append(point)

        async with async_session_maker() as session:
            public_file = PublicFiles(hash=file_hash, presentation_name=file_name, is_prepared=True)
            session.add(public_file)

            pubic_files_dir = Path("files/public")
            pubic_files_dir.mkdir(exist_ok=True)
            file_destination = pubic_files_dir / file_hash_str
            with open(file_destination, "wb") as file:
                file.write(file_content)

            await qdrant_client.upsert(collection_name=VECTOR_DB_PUBLIC_COLLECTION_NAME, points=points)

            await session.commit()


async def main():
    await initialize_vector_db()
    await fulfill_public_collection()


if __name__ == "__main__":
    asyncio.run(main())

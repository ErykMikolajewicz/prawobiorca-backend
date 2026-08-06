import asyncio
import sys
import uuid
from pathlib import Path

sys.path.append("")

import httpx2
from sqlalchemy import insert

from app.application.services.embedding import DocumentEmbedder
from app.application.services.regulations import RegulationPreparator
from app.infrastructure.relational_db.connection import async_session_maker
from app.infrastructure.relational_db.schemas.documents import RegulationsDocuments
from app.infrastructure.relational_db.schemas.regulations import regulations_table

# Unused import necessary for sqlalchemy
from app.infrastructure.relational_db.schemas.users import users_table  # noqa: F401
from app.infrastructure.text_transformator.regulation_splitter import RegulationSplitter
from app.infrastructure.text_transformator.text_embedder import TextsEmbedder
from app.shared.settings.text_transformator import text_transformator_settings


async def init_regulations():
    init_files_dir = Path("cicd/init/files")

    async with httpx2.AsyncClient(timeout=900) as client:
        texts_embedder = TextsEmbedder(
            client=client,
            texts_transformator_url=text_transformator_settings.URL,
        )
        regulation_splitter = RegulationSplitter(
            client=client,
            texts_transformator_url=text_transformator_settings.URL,
        )
        document_embedder = DocumentEmbedder(texts_embedder)
        regulation_preparator = RegulationPreparator(
            regulation_splitter,
            document_embedder,
        )

        for file_path in init_files_dir.iterdir():
            file_name = file_path.name

            with open(file_path, "rb") as file:
                file_content = file.read()

            regulation_id = uuid.uuid4()

            documents_to_embed = await regulation_preparator.prepare_regulation(file_content)
            print(f"Embedded regulation: {file_name}")

            regulation_documents = []

            for documents_batch in documents_to_embed.get_batch_iterator():
                for document in documents_batch:
                    regulation_documents.append(
                        {
                            "id": document.id,
                            "user_id": None,
                            "header": document.title,
                            "text": document.text,
                            "chunk_order": document.chunk_order,
                            "vector": document.vector,
                            "regulation_id": regulation_id,
                        }
                    )

            async with async_session_maker.begin() as session:
                await session.execute(
                    insert(regulations_table),
                    [
                        {
                            "id": regulation_id,
                            "presentation_name": file_name,
                            "is_prepared": True,
                            "user_id": None,
                        }
                    ],
                )

                await session.execute(
                    insert(RegulationsDocuments),
                    regulation_documents,
                )

                public_files_dir = Path("regulations")
                public_files_dir.mkdir(exist_ok=True)

                file_destination = public_files_dir / str(regulation_id)
                with open(file_destination, "wb") as file:
                    file.write(file_content)

            print(f"Saved regulation: {file_name}, ")


async def main():
    await init_regulations()


if __name__ == "__main__":
    asyncio.run(main())

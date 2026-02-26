import uuid
from dataclasses import dataclass

from app.application.interfaces.file_storage import StorageRepository
from app.application.interfaces.regulations import RegulationsRepository
from app.application.ports.embeddings import EmbeddingPort
from app.domain.services.texts_extraction import extract_document


@dataclass
class PrepareUserFile:
    embedding_port: EmbeddingPort
    storage_repository: StorageRepository
    regulations_repository: RegulationsRepository
    file_name: str

    async def execute(self):
        file_data = await self.storage_repository.get_file(self.file_name)

        document = extract_document(file_data, self.file_name)
        await self.regulations_repository.initialize_law_act(self.file_name)

        for chapter in document.chapters:
            chapter_title = chapter.title
            points = []
            for paragraph in chapter.paragraphs:
                for point in paragraph.points:
                    points.append(point.body)
            vectors = await self.embedding_port.embed_documents(points, chapter_title)

            for point, vector in zip(points, vectors, strict=True):
                point_id = uuid.uuid4()
                payload = {"text": point}
                await self.regulations_repository.add_point(point_id, vector, payload)

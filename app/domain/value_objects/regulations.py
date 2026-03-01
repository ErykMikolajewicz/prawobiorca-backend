from dataclasses import dataclass

from app.domain.value_objects.preparation import DocumentToEmbed


@dataclass
class Point:
    number: int
    body: str


@dataclass
class Paragraph:
    title: str
    number: int
    points: list[Point]


@dataclass
class Chapter:
    title: str
    number: int
    paragraphs: list[Paragraph]


@dataclass
class RegulationAct:
    name: str
    _chapters: list[Chapter]

    def get_documents_to_embed(self) -> list[DocumentToEmbed]:
        documents = []
        for chapter in self._chapters:
            chapter_title = chapter.title
            for paragraph in chapter.paragraphs:
                for point in paragraph.points:
                    document_to_embed = DocumentToEmbed(chapter_title, point.body)
                    documents.append(document_to_embed)
        return documents

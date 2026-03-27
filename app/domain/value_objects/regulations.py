from dataclasses import dataclass
from enum import StrEnum

from app.domain.value_objects.documents import Document


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

    def get_documents_to_embed(self) -> list[Document]:
        documents = []
        for chapter in self._chapters:
            for paragraph in chapter.paragraphs:
                paragraph_title = paragraph.title
                for point in paragraph.points:
                    document_to_embed = Document(paragraph_title, point.body)
                    documents.append(document_to_embed)
        return documents


class UsefulLabels(StrEnum):
    SECTION_HEADER = "section_header"
    LIST_ITEM = "list_item"
    TEXT = "text"


@dataclass
class RegulationElement:
    label: str
    text: str
    tokens_number: int

from collections.abc import Iterable
from dataclasses import dataclass, field
from enum import StrEnum

from app.domain.exceptions.documents import ToLongDocument, ToLongHeaderSection
from app.domain.value_objects.documents import Document, DocumentsCollection
from app.shared.settings.application import app_settings
from app.shared.settings.text_transformator import text_transformator_settings


@dataclass
class HeaderSection:
    _header_elements: list[RegulationElement] = field(default_factory=list, init=False)
    _other_elements: list[RegulationElement] = field(default_factory=list, init=False)
    _header_text: str = field(default="", init=False)
    _header_tokens: int = field(default=text_transformator_settings.MAX_TITLE_TOKENS_OVERHEAD, init=False)

    def add_header_element(self, header_element: RegulationElement):
        self._header_elements.append(header_element)

        self._header_tokens += header_element.tokens_number
        self._header_text += header_element.text

        if self._header_tokens > text_transformator_settings.MAX_TOKENS:
            raise ToLongHeaderSection()

    def add_other_element(self, other_element: RegulationElement):
        self._other_elements.append(other_element)

    def create_section_documents(self) -> list[Document]:
        documents = []
        document_tokens = self._header_tokens
        document_text = ""
        elements_count = len(self._other_elements)
        for index, element in enumerate(self._other_elements):
            document_tokens += element.tokens_number
            if document_tokens > text_transformator_settings.MAX_TOKENS:
                raise ToLongDocument

            document_text += element.text

            is_last_element = index == elements_count - 1
            if is_last_element:
                document = Document(self._header_text, document_text)
                documents.append(document)
                break

            next_element = self._other_elements[index + 1]
            tokens_with_next = document_tokens + next_element.tokens_number
            if tokens_with_next > app_settings.DOCUMENT_DESIRED_TOKENS_LENGTH:
                document = Document(self._header_text, document_text)
                documents.append(document)
                document_text = ""
                document_tokens = self._header_tokens

        return documents

    def filter_useful_elements(self):
        useful_elements = []
        for element in self._other_elements:
            match element.label:
                case UsefulLabels.TEXT | UsefulLabels.LIST_ITEM:
                    useful_elements.append(element)
        self._other_elements = useful_elements


@dataclass
class RegulationAct:
    _elements: Iterable[RegulationElement]

    def get_documents_to_embed(self) -> DocumentsCollection:

        grouped_elements = self._group_elements_by_headers()

        documents = []
        for header_section in grouped_elements:
            header_section.filter_useful_elements()
            section_documents = header_section.create_section_documents()
            documents.extend(section_documents)

        for index, document in enumerate(documents):
            document.chunk_order = index

        return DocumentsCollection(documents)

    def _group_elements_by_headers(self) -> list[HeaderSection]:
        header_sections = []
        last_element_type = None
        current_section = HeaderSection()
        for element in self._elements:
            match element.label:
                case UsefulLabels.SECTION_HEADER:
                    if last_element_type == UsefulLabels.SECTION_HEADER or last_element_type is None:
                        current_section.add_header_element(element)
                    else:
                        header_sections.append(current_section)
                        current_section = HeaderSection()
                        current_section.add_header_element(element)
                case _:
                    current_section.add_other_element(element)

            last_element_type = element.label

        if current_section._header_elements or current_section._other_elements:
            header_sections.append(current_section)

        return header_sections


class RegulationType(StrEnum):
    ACT = "ACT"
    DECREE = "DECREE"
    STATUTE = "STATUTE"


@dataclass
class RegulationElement:
    label: str
    text: str
    tokens_number: int


class UsefulLabels(StrEnum):
    SECTION_HEADER = "section_header"
    LIST_ITEM = "list_item"
    TEXT = "text"


@dataclass
class RegulationRegistrationData:
    presentation_name: str
    regulation_type: RegulationType | None = None

from typing import Callable

from docling.datamodel.document import TextItem
from src.models import DocumentWithTokens


def add_tokens_info(documents: list[TextItem], tokens_counter: Callable[[str], int]) -> list[DocumentWithTokens]:

    documents_with_tokens = []
    for document in documents:
        label = document.label
        text = document.orig
        tokens_number = tokens_counter(text)
        document_with_tokens = DocumentWithTokens(label=label, text=text, tokens_number=tokens_number)
        documents_with_tokens.append(document_with_tokens)

    return documents_with_tokens

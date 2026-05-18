from dataclasses import dataclass

from app.domain.value_objects.documents import DocumentType


@dataclass
class FileRegistrationData:
    hash: bytes
    presentation_name: str
    document_type: DocumentType | None = None

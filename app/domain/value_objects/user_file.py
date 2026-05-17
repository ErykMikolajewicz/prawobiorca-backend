from dataclasses import dataclass

from app.framework.dependencies.document_types import DocumentType


@dataclass
class FileRegistrationData:
    hash: bytes
    presentation_name: str
    document_type: DocumentType | None = None

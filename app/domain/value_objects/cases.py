from dataclasses import dataclass


@dataclass
class CaseData:
    id: str
    name: str


@dataclass
class CaseArticleData:
    id: str
    case_id: str
    document_name: str
    article_content: str

from uuid import UUID

from pydantic import BaseModel, Field


class NewCase(BaseModel):
    user_id: UUID
    name: str = Field(min_length=1)


class NewCaseArticle(BaseModel):
    case_id: UUID
    document_name: str = Field(min_length=1)
    article_content: str = Field(min_length=1)

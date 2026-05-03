from uuid import UUID

from pydantic import BaseModel, Field

from app.shared.consts import MAX_FILENAME_LENGTH, MIN_FILENAME_LENGTH


class NewCase(BaseModel):
    user_id: UUID
    name: str = Field(min_length=1)


class NewCaseArticle(BaseModel):
    presentation_name: str = Field(min_length=1, alias="presentationName")
    content: str = Field(min_length=1)


class CaseData(BaseModel):
    id: UUID
    name: str


class CaseArticleData(BaseModel):
    id: UUID
    case_id: UUID = Field(alias="caseId")
    presentation_name: str = Field(
        min_length=MIN_FILENAME_LENGTH, max_length=MAX_FILENAME_LENGTH, alias="presentationName"
    )
    content: str = Field(min_length=1)

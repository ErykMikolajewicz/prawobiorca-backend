from pydantic import BaseModel, Field


class AccountCreate(BaseModel):
    login: str = Field(max_length=256)
    password: str = Field(max_length=256)

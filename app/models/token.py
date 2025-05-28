from pydantic import BaseModel

from app.core.enums import TokenType


class AccessToken(BaseModel):
    access_token: str
    expires_in: int
    token_type: TokenType

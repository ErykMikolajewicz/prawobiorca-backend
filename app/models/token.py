from typing import Annotated

from pydantic import BaseModel
from pydantic.types import StringConstraints

from app.core.enums import TokenType
from app.core.consts import BEARER_TOKEN_LENGTH


class AccessToken(BaseModel):
    access_token: Annotated[str, StringConstraints(min_length=BEARER_TOKEN_LENGTH , max_length=BEARER_TOKEN_LENGTH )]
    expires_in: int
    token_type: TokenType
